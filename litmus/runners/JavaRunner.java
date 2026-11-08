package litmus.runner;

import java.io.File;
import java.io.IOException;
import java.io.PrintStream;
import java.lang.reflect.Constructor;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.net.URL;
import java.net.URLClassLoader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.stream.Stream;

public class JavaRunner {

    private static String escapeJson(String s) {
        if (s == null) {
            return "";
        }
        StringBuilder sb = new StringBuilder(s.length() + 16);
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            switch (c) {
                case '\\':
                    sb.append("\\\\");
                    break;
                case '"':
                    sb.append("\\\"");
                    break;
                case '\b':
                    sb.append("\\b");
                    break;
                case '\f':
                    sb.append("\\f");
                    break;
                case '\n':
                    sb.append("\\n");
                    break;
                case '\r':
                    sb.append("\\r");
                    break;
                case '\t':
                    sb.append("\\t");
                    break;
                default:
                    if (c < 0x20) {
                        sb.append(String.format("\\u%04x", (int) c));
                    } else {
                        sb.append(c);
                    }
            }
        }
        return sb.toString();
    }

    private static void emitJson(PrintStream out, String id, String status, String message) {
        out.println(
            "{\"id\":\"" + escapeJson(id)
            + "\",\"status\":\"" + escapeJson(status)
            + "\",\"message\":\"" + escapeJson(message) + "\"}"
        );
        out.flush();
    }

    private static ExecutorService newDaemonExecutor() {
        return Executors.newSingleThreadExecutor(r -> {
            Thread t = new Thread(r, "litmus-java-test");
            t.setDaemon(true);
            return t;
        });
    }

    private static Set<String> loadTestsFilter(String pathStr) throws IOException {
        if (pathStr == null || pathStr.isEmpty()) {
            return null;
        }
        Set<String> ids = new HashSet<>();
        for (String line : Files.readAllLines(Paths.get(pathStr), StandardCharsets.UTF_8)) {
            String trimmed = line.trim();
            if (!trimmed.isEmpty()) {
                ids.add(trimmed);
            }
        }
        return ids;
    }

    private static Map<String, Double> loadTimeouts(String pathStr) throws IOException {
        Map<String, Double> map = new HashMap<>();
        if (pathStr == null || pathStr.isEmpty()) {
            return map;
        }
        for (String line : Files.readAllLines(Paths.get(pathStr), StandardCharsets.UTF_8)) {
            String trimmed = line.trim();
            if (trimmed.isEmpty()) {
                continue;
            }
            int tab = trimmed.lastIndexOf('\t');
            if (tab > 0) {
                String id = trimmed.substring(0, tab);
                double sec = Double.parseDouble(trimmed.substring(tab + 1));
                map.put(id, sec);
            }
        }
        return map;
    }

    private static List<String> discoverClassNames(Path classesDir) throws IOException {
        List<String> names = new ArrayList<>();
        try (Stream<Path> stream = Files.walk(classesDir)) {
            stream.filter(Files::isRegularFile)
                  .filter(p -> p.toString().endsWith(".class"))
                  .forEach(p -> {
                      String rel = classesDir.relativize(p).toString();
                      if (rel.contains("$")) {
                          return;
                      }
                      String clsName = rel.substring(0, rel.length() - 6)
                                          .replace(File.separatorChar, '.');
                      names.add(clsName);
                  });
        }
        Collections.sort(names);
        return names;
    }

    private static Method findOptionalNoArg(Class<?> cls, String name) {
        try {
            Method m = cls.getMethod(name);
            if (!Modifier.isStatic(m.getModifiers())) {
                return m;
            }
        } catch (NoSuchMethodException ignored) {
        }
        return null;
    }

    public static void main(String[] args) throws Exception {
        String classesDirArg = null;
        String testsFile = null;
        String timeoutsFile = null;
        for (int i = 0; i < args.length; i++) {
            if ("--classes".equals(args[i]) && i + 1 < args.length) {
                classesDirArg = args[++i];
            } else if ("--tests-file".equals(args[i]) && i + 1 < args.length) {
                testsFile = args[++i];
            } else if ("--timeouts-file".equals(args[i]) && i + 1 < args.length) {
                timeoutsFile = args[++i];
            }
        }
        if (classesDirArg == null) {
            System.err.println("缺少 --classes 参数");
            System.exit(2);
        }

        PrintStream realOut = System.out;
        System.setOut(System.err);

        Path classesDir = Paths.get(classesDirArg).toAbsolutePath();
        Set<String> allowedIds = loadTestsFilter(testsFile);
        Map<String, Double> timeouts = loadTimeouts(timeoutsFile);
        List<String> classNames = discoverClassNames(classesDir);

        ExecutorService executor = newDaemonExecutor();
        try (URLClassLoader loader = new URLClassLoader(
                new URL[]{classesDir.toUri().toURL()},
                JavaRunner.class.getClassLoader())) {

            for (String clsName : classNames) {
                Class<?> cls = Class.forName(clsName, false, loader);
                if (cls.isInterface() || Modifier.isAbstract(cls.getModifiers())) {
                    continue;
                }
                String simpleName = cls.getSimpleName();
                if (!(simpleName.endsWith("Test") || simpleName.endsWith("Tests") || simpleName.startsWith("Test"))) {
                    continue;
                }

                List<Method> testMethods = new ArrayList<>();
                for (Method m : cls.getMethods()) {
                    if (m.getName().startsWith("test")
                            && m.getParameterCount() == 0
                            && m.getReturnType() == void.class
                            && !Modifier.isStatic(m.getModifiers())) {
                        testMethods.add(m);
                    }
                }
                if (testMethods.isEmpty()) {
                    continue;
                }
                testMethods.sort(Comparator.comparing(Method::getName));

                Method setUpMethod = findOptionalNoArg(cls, "setUp");
                Method tearDownMethod = findOptionalNoArg(cls, "tearDown");
                Constructor<?> ctor = cls.getDeclaredConstructor();
                ctor.setAccessible(true);

                for (Method m : testMethods) {
                    String testId = cls.getName() + "#" + m.getName();
                    if (allowedIds != null && !allowedIds.contains(testId)) {
                        continue;
                    }

                    Callable<Void> task = () -> {
                        Object instance = ctor.newInstance();
                        try {
                            if (setUpMethod != null) {
                                setUpMethod.invoke(instance);
                            }
                            m.invoke(instance);
                        } finally {
                            if (tearDownMethod != null) {
                                tearDownMethod.invoke(instance);
                            }
                        }
                        return null;
                    };

                    Double timeoutSec = timeouts.get(testId);
                    Future<Void> future = executor.submit(task);
                    try {
                        if (timeoutSec != null && timeoutSec > 0) {
                            long ms = Math.max(1L, (long) (timeoutSec * 1000.0));
                            future.get(ms, TimeUnit.MILLISECONDS);
                        } else {
                            future.get();
                        }
                        emitJson(realOut, testId, "pass", "");
                    } catch (TimeoutException te) {
                        future.cancel(true);
                        executor.shutdownNow();
                        executor = newDaemonExecutor();
                        emitJson(realOut, testId, "timeout", "用例超时 (" + timeoutSec + "s)");
                    } catch (ExecutionException ee) {
                        Throwable cause = ee.getCause();
                        if (cause instanceof InvocationTargetException && cause.getCause() != null) {
                            cause = cause.getCause();
                        }
                        if (cause instanceof AssertionError) {
                            emitJson(realOut, testId, "fail", String.valueOf(cause));
                        } else {
                            emitJson(realOut, testId, "error", String.valueOf(cause));
                        }
                    } catch (InterruptedException ie) {
                        Thread.currentThread().interrupt();
                        emitJson(realOut, testId, "error", "测试线程被中断");
                    }
                }
            }
        } finally {
            executor.shutdownNow();
        }
        System.exit(0);
    }
}
