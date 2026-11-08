package com.litmus.ticket;

import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.regex.Pattern;

/**
 * 轻量级内存 JDBC 数据库引擎，用于模拟真实 SQL 解析与参数绑定行为。
 */
public final class InMemoryTicketDb {
    private static final List<String> SCHEMA_COLS = Arrays.asList(
            "id", "title", "assignee", "status", "priority", "note");

    private final List<Map<String, Object>> rows = new ArrayList<>();

    public void insert(Ticket t) {
        Map<String, Object> row = new LinkedHashMap<>();
        row.put("id", Integer.valueOf(t.id()));
        row.put("title", t.title());
        row.put("assignee", t.assignee());
        row.put("status", t.status());
        row.put("priority", Integer.valueOf(t.priority()));
        row.put("note", t.note());
        rows.add(row);
    }

    public Ticket getById(int id) {
        for (Map<String, Object> row : rows) {
            if (((Integer) row.get("id")).intValue() == id) {
                return toTicket(row);
            }
        }
        return null;
    }

    public List<Ticket> allTickets() {
        List<Ticket> out = new ArrayList<>();
        for (Map<String, Object> row : rows) {
            out.add(toTicket(row));
        }
        out.sort(Comparator.comparingInt(Ticket::id));
        return Collections.unmodifiableList(out);
    }

    private static Ticket toTicket(Map<String, Object> row) {
        return new Ticket(
                ((Integer) row.get("id")).intValue(),
                (String) row.get("title"),
                (String) row.get("assignee"),
                (String) row.get("status"),
                ((Integer) row.get("priority")).intValue(),
                (String) row.get("note"));
    }

    public Connection openConnection() {
        final boolean[] closed = new boolean[] { false };
        return (Connection) Proxy.newProxyInstance(
                Connection.class.getClassLoader(),
                new Class<?>[] { Connection.class },
                (proxy, method, args) -> {
                    String name = method.getName();
                    if ("toString".equals(name)) {
                        return "InMemoryConnection";
                    }
                    if ("hashCode".equals(name)) {
                        return System.identityHashCode(proxy);
                    }
                    if ("equals".equals(name)) {
                        return Boolean.valueOf(proxy == args[0]);
                    }
                    if ("close".equals(name)) {
                        closed[0] = true;
                        return null;
                    }
                    if ("isClosed".equals(name)) {
                        return Boolean.valueOf(closed[0]);
                    }
                    if (closed[0]) {
                        throw new SQLException("Connection is closed");
                    }
                    if ("createStatement".equals(name)) {
                        return createStatementProxy();
                    }
                    if ("prepareStatement".equals(name) && args != null && args.length >= 1) {
                        return createPreparedStatementProxy((String) args[0]);
                    }
                    throw new UnsupportedOperationException("Unsupported Connection method: " + name);
                });
    }

    private Statement createStatementProxy() {
        final boolean[] closed = new boolean[] { false };
        return (Statement) Proxy.newProxyInstance(
                Statement.class.getClassLoader(),
                new Class<?>[] { Statement.class },
                (proxy, method, args) -> {
                    String name = method.getName();
                    if ("toString".equals(name)) {
                        return "InMemoryStatement";
                    }
                    if ("hashCode".equals(name)) {
                        return System.identityHashCode(proxy);
                    }
                    if ("equals".equals(name)) {
                        return Boolean.valueOf(proxy == args[0]);
                    }
                    if ("close".equals(name)) {
                        closed[0] = true;
                        return null;
                    }
                    if ("isClosed".equals(name)) {
                        return Boolean.valueOf(closed[0]);
                    }
                    if (closed[0]) {
                        throw new SQLException("Statement is closed");
                    }
                    if ("executeQuery".equals(name) && args != null && args.length == 1) {
                        return executeSelect((String) args[0], Collections.emptyMap());
                    }
                    if ("executeUpdate".equals(name) && args != null && args.length == 1) {
                        return Integer.valueOf(executeUpdate((String) args[0], Collections.emptyMap()));
                    }
                    throw new UnsupportedOperationException("Unsupported Statement method: " + name);
                });
    }

    private PreparedStatement createPreparedStatementProxy(String sql) throws SQLException {
        if (sql == null || sql.trim().isEmpty()) {
            throw new SQLException("SQL 不能为空");
        }
        final boolean[] closed = new boolean[] { false };
        final Map<Integer, Object> params = new HashMap<>();
        return (PreparedStatement) Proxy.newProxyInstance(
                PreparedStatement.class.getClassLoader(),
                new Class<?>[] { PreparedStatement.class },
                (proxy, method, args) -> {
                    String name = method.getName();
                    if ("toString".equals(name)) {
                        return "InMemoryPreparedStatement(" + sql + ")";
                    }
                    if ("hashCode".equals(name)) {
                        return System.identityHashCode(proxy);
                    }
                    if ("equals".equals(name)) {
                        return Boolean.valueOf(proxy == args[0]);
                    }
                    if ("close".equals(name)) {
                        closed[0] = true;
                        return null;
                    }
                    if ("isClosed".equals(name)) {
                        return Boolean.valueOf(closed[0]);
                    }
                    if (closed[0]) {
                        throw new SQLException("PreparedStatement is closed");
                    }
                    if (("setString".equals(name) || "setInt".equals(name) || "setObject".equals(name))
                            && args != null && args.length >= 2) {
                        params.put((Integer) args[0], args[1]);
                        return null;
                    }
                    if ("clearParameters".equals(name)) {
                        params.clear();
                        return null;
                    }
                    if ("executeQuery".equals(name) && (args == null || args.length == 0)) {
                        return executeSelect(sql, params);
                    }
                    if ("executeUpdate".equals(name) && (args == null || args.length == 0)) {
                        return Integer.valueOf(executeUpdate(sql, params));
                    }
                    throw new UnsupportedOperationException("Unsupported PreparedStatement method: " + name);
                });
    }

    private ResultSet createResultSetProxy(List<String> cols, List<Map<String, Object>> resultRows) {
        final boolean[] closed = new boolean[] { false };
        final int[] cursor = new int[] { -1 };
        return (ResultSet) Proxy.newProxyInstance(
                ResultSet.class.getClassLoader(),
                new Class<?>[] { ResultSet.class },
                (proxy, method, args) -> {
                    String name = method.getName();
                    if ("toString".equals(name)) {
                        return "InMemoryResultSet";
                    }
                    if ("hashCode".equals(name)) {
                        return System.identityHashCode(proxy);
                    }
                    if ("equals".equals(name)) {
                        return Boolean.valueOf(proxy == args[0]);
                    }
                    if ("close".equals(name)) {
                        closed[0] = true;
                        return null;
                    }
                    if ("isClosed".equals(name)) {
                        return Boolean.valueOf(closed[0]);
                    }
                    if (closed[0]) {
                        throw new SQLException("ResultSet is closed");
                    }
                    if ("next".equals(name)) {
                        cursor[0]++;
                        return Boolean.valueOf(cursor[0] < resultRows.size());
                    }
                    if (cursor[0] < 0 || cursor[0] >= resultRows.size()) {
                        throw new SQLException("ResultSet cursor out of bounds");
                    }
                    Map<String, Object> cur = resultRows.get(cursor[0]);
                    if (("getString".equals(name) || "getInt".equals(name) || "getObject".equals(name))
                            && args != null && args.length == 1) {
                        String colName;
                        if (args[0] instanceof Integer) {
                            int idx = ((Integer) args[0]).intValue() - 1;
                            if (idx < 0 || idx >= cols.size()) {
                                throw new SQLException("Invalid column index: " + args[0]);
                            }
                            colName = cols.get(idx);
                        } else {
                            colName = ((String) args[0]).toLowerCase(Locale.ROOT);
                            if (!cols.contains(colName)) {
                                throw new SQLException("Column not in projection: " + colName);
                            }
                        }
                        Object val = cur.get(colName);
                        if ("getInt".equals(name)) {
                            return Integer.valueOf(val == null ? 0 : ((Number) val).intValue());
                        }
                        if ("getString".equals(name)) {
                            return val == null ? null : String.valueOf(val);
                        }
                        return val;
                    }
                    throw new UnsupportedOperationException("Unsupported ResultSet method: " + name);
                });
    }

    private enum TokType {
        IDENT, STRING, NUMBER, PARAM, COMMA, EQ, GE, GT, STAR, EOF
    }

    private static final class Token {
        final TokType type;
        final String text;
        final Object value;

        Token(TokType type, String text, Object value) {
            this.type = type;
            this.text = text;
            this.value = value;
        }
    }

    private static List<Token> tokenize(String sql, Map<Integer, Object> params) throws SQLException {
        List<Token> tokens = new ArrayList<>();
        int i = 0;
        int n = sql.length();
        int paramSeq = 0;
        while (i < n) {
            char c = sql.charAt(i);
            if (Character.isWhitespace(c)) {
                i++;
                continue;
            }
            if (c == '-' && i + 1 < n && sql.charAt(i + 1) == '-') {
                while (i < n && sql.charAt(i) != '\n') {
                    i++;
                }
                continue;
            }
            if (c == ';') {
                i++;
                continue;
            }
            if (c == ',') {
                tokens.add(new Token(TokType.COMMA, ",", null));
                i++;
                continue;
            }
            if (c == '*') {
                tokens.add(new Token(TokType.STAR, "*", null));
                i++;
                continue;
            }
            if (c == '=') {
                tokens.add(new Token(TokType.EQ, "=", null));
                i++;
                continue;
            }
            if (c == '>') {
                if (i + 1 < n && sql.charAt(i + 1) == '=') {
                    tokens.add(new Token(TokType.GE, ">=", null));
                    i += 2;
                } else {
                    tokens.add(new Token(TokType.GT, ">", null));
                    i++;
                }
                continue;
            }
            if (c == '?') {
                paramSeq++;
                if (!params.containsKey(Integer.valueOf(paramSeq))) {
                    throw new SQLException("Missing bound parameter at index " + paramSeq);
                }
                tokens.add(new Token(TokType.PARAM, "?", params.get(Integer.valueOf(paramSeq))));
                i++;
                continue;
            }
            if (c == '\'') {
                StringBuilder sb = new StringBuilder();
                i++;
                boolean closed = false;
                while (i < n) {
                    char ch = sql.charAt(i);
                    if (ch == '\'') {
                        if (i + 1 < n && sql.charAt(i + 1) == '\'') {
                            sb.append('\'');
                            i += 2;
                            continue;
                        }
                        closed = true;
                        i++;
                        break;
                    }
                    sb.append(ch);
                    i++;
                }
                if (!closed) {
                    throw new SQLException("Unterminated SQL string literal near: " + sql);
                }
                tokens.add(new Token(TokType.STRING, sb.toString(), sb.toString()));
                continue;
            }
            if (Character.isDigit(c) || (c == '-' && i + 1 < n && Character.isDigit(sql.charAt(i + 1)))) {
                int start = i;
                i++;
                while (i < n && Character.isDigit(sql.charAt(i))) {
                    i++;
                }
                String numStr = sql.substring(start, i);
                tokens.add(new Token(TokType.NUMBER, numStr, Integer.valueOf(Integer.parseInt(numStr))));
                continue;
            }
            if (Character.isLetter(c) || c == '_') {
                int start = i;
                while (i < n && (Character.isLetterOrDigit(sql.charAt(i)) || sql.charAt(i) == '_')) {
                    i++;
                }
                String word = sql.substring(start, i);
                tokens.add(new Token(TokType.IDENT, word.toUpperCase(Locale.ROOT), word));
                continue;
            }
            throw new SQLException("Unexpected SQL token char '" + c + "' in: " + sql);
        }
        tokens.add(new Token(TokType.EOF, "", null));
        return tokens;
    }

    private static final class Parser {
        final List<Token> tokens;
        int pos = 0;

        Parser(List<Token> tokens) {
            this.tokens = tokens;
        }

        Token peek() {
            return tokens.get(pos);
        }

        boolean isKeyword(String kw) {
            Token t = peek();
            return t.type == TokType.IDENT && kw.equals(t.text);
        }

        Token consume() {
            return tokens.get(pos++);
        }

        void expectKeyword(String kw) throws SQLException {
            if (!isKeyword(kw)) {
                throw new SQLException("Expected SQL keyword " + kw + ", got " + peek().text);
            }
            consume();
        }

        ValueExpr parseValue() throws SQLException {
            Token t = consume();
            if (t.type == TokType.STRING || t.type == TokType.NUMBER || t.type == TokType.PARAM) {
                return new ValueExpr(false, null, t.value);
            }
            if (t.type == TokType.IDENT) {
                String col = ((String) t.value).toLowerCase(Locale.ROOT);
                if (!SCHEMA_COLS.contains(col)) {
                    throw new SQLException("Unknown column: " + col);
                }
                return new ValueExpr(true, col, null);
            }
            throw new SQLException("Unexpected value token: " + t.text);
        }

        Pred parseOr() throws SQLException {
            Pred left = parseAnd();
            while (isKeyword("OR")) {
                consume();
                Pred right = parseAnd();
                final Pred lhs = left;
                left = row -> lhs.eval(row) || right.eval(row);
            }
            return left;
        }

        Pred parseAnd() throws SQLException {
            Pred left = parseAtom();
            while (isKeyword("AND")) {
                consume();
                Pred right = parseAtom();
                final Pred lhs = left;
                left = row -> lhs.eval(row) && right.eval(row);
            }
            return left;
        }

        Pred parseAtom() throws SQLException {
            ValueExpr left = parseValue();
            if (isKeyword("LIKE")) {
                consume();
                ValueExpr patternExpr = parseValue();
                char escapeChar = 0;
                boolean hasEscape = false;
                if (isKeyword("ESCAPE")) {
                    consume();
                    Token escTok = consume();
                    if (escTok.type != TokType.STRING && escTok.type != TokType.PARAM) {
                        throw new SQLException("ESCAPE must be a single character string");
                    }
                    String escStr = String.valueOf(escTok.value);
                    if (escStr.length() != 1) {
                        throw new SQLException("ESCAPE string must have length 1");
                    }
                    escapeChar = escStr.charAt(0);
                    hasEscape = true;
                }
                final char esc = escapeChar;
                final boolean useEsc = hasEscape;
                return row -> {
                    Object lv = left.eval(row);
                    Object pv = patternExpr.eval(row);
                    if (lv == null || pv == null) {
                        return false;
                    }
                    return matchLike(String.valueOf(lv), String.valueOf(pv), useEsc, esc);
                };
            }
            Token op = consume();
            ValueExpr right = parseValue();
            if (op.type == TokType.EQ) {
                return row -> compareEqual(left.eval(row), right.eval(row));
            }
            if (op.type == TokType.GE) {
                return row -> compareNumeric(left.eval(row), right.eval(row)) >= 0;
            }
            if (op.type == TokType.GT) {
                return row -> compareNumeric(left.eval(row), right.eval(row)) > 0;
            }
            throw new SQLException("Unsupported operator: " + op.text);
        }
    }

    private interface Pred {
        boolean eval(Map<String, Object> row) throws SQLException;
    }

    private static final class ValueExpr {
        final boolean isColumn;
        final String column;
        final Object literal;

        ValueExpr(boolean isColumn, String column, Object literal) {
            this.isColumn = isColumn;
            this.column = column;
            this.literal = literal;
        }

        Object eval(Map<String, Object> row) {
            return isColumn ? row.get(column) : literal;
        }
    }

    private static boolean compareEqual(Object a, Object b) {
        if (a == null || b == null) {
            return a == b;
        }
        if (a instanceof Number && b instanceof Number) {
            return ((Number) a).intValue() == ((Number) b).intValue();
        }
        return String.valueOf(a).equals(String.valueOf(b));
    }

    private static int compareNumeric(Object a, Object b) throws SQLException {
        if (a instanceof Number && b instanceof Number) {
            return Integer.compare(((Number) a).intValue(), ((Number) b).intValue());
        }
        throw new SQLException("Numeric comparison requires integer operands");
    }

    private static boolean matchLike(String text, String pattern, boolean hasEscape, char escapeChar) {
        StringBuilder regex = new StringBuilder("^");
        int n = pattern.length();
        for (int i = 0; i < n; i++) {
            char c = pattern.charAt(i);
            if (hasEscape && c == escapeChar && i + 1 < n) {
                char next = pattern.charAt(++i);
                regex.append(Pattern.quote(String.valueOf(next)));
            } else if (c == '%') {
                regex.append(".*");
            } else if (c == '_') {
                regex.append(".");
            } else {
                regex.append(Pattern.quote(String.valueOf(c)));
            }
        }
        regex.append("$");
        return Pattern.compile(regex.toString(), Pattern.DOTALL).matcher(text).matches();
    }

    private ResultSet executeSelect(String sql, Map<Integer, Object> params) throws SQLException {
        List<Token> tokens = tokenize(sql, params);
        Parser p = new Parser(tokens);
        p.expectKeyword("SELECT");
        List<String> cols = new ArrayList<>();
        if (p.peek().type == TokType.STAR) {
            p.consume();
            cols.addAll(SCHEMA_COLS);
        } else {
            while (true) {
                Token colTok = p.consume();
                if (colTok.type != TokType.IDENT) {
                    throw new SQLException("Expected column name, got " + colTok.text);
                }
                String col = ((String) colTok.value).toLowerCase(Locale.ROOT);
                if (!SCHEMA_COLS.contains(col)) {
                    throw new SQLException("Unknown column: " + col);
                }
                cols.add(col);
                if (p.peek().type == TokType.COMMA) {
                    p.consume();
                } else {
                    break;
                }
            }
        }
        p.expectKeyword("FROM");
        p.expectKeyword("TICKETS");
        Pred pred = row -> true;
        if (p.isKeyword("WHERE")) {
            p.consume();
            pred = p.parseOr();
        }
        boolean orderById = false;
        boolean desc = false;
        if (p.isKeyword("ORDER")) {
            p.consume();
            p.expectKeyword("BY");
            Token orderCol = p.consume();
            if (orderCol.type != TokType.IDENT || !"ID".equals(orderCol.text)) {
                throw new SQLException("Only ORDER BY id is supported");
            }
            orderById = true;
            if (p.isKeyword("ASC")) {
                p.consume();
            } else if (p.isKeyword("DESC")) {
                p.consume();
                desc = true;
            }
        }
        if (p.peek().type != TokType.EOF) {
            throw new SQLException("Unexpected trailing SQL token: " + p.peek().text);
        }

        List<Map<String, Object>> matched = new ArrayList<>();
        for (Map<String, Object> row : rows) {
            if (pred.eval(row)) {
                matched.add(new LinkedHashMap<>(row));
            }
        }
        if (orderById) {
            final boolean isDesc = desc;
            matched.sort((a, b) -> {
                int cmp = Integer.compare(((Integer) a.get("id")).intValue(), ((Integer) b.get("id")).intValue());
                return isDesc ? -cmp : cmp;
            });
        }
        return createResultSetProxy(cols, matched);
    }

    private int executeUpdate(String sql, Map<Integer, Object> params) throws SQLException {
        List<Token> tokens = tokenize(sql, params);
        Parser p = new Parser(tokens);
        p.expectKeyword("UPDATE");
        p.expectKeyword("TICKETS");
        p.expectKeyword("SET");

        List<Map.Entry<String, ValueExpr>> assignments = new ArrayList<>();
        while (true) {
            Token colTok = p.consume();
            if (colTok.type != TokType.IDENT) {
                throw new SQLException("Expected column in SET clause");
            }
            String col = ((String) colTok.value).toLowerCase(Locale.ROOT);
            if (!SCHEMA_COLS.contains(col) || "id".equals(col)) {
                throw new SQLException("Column cannot be updated: " + col);
            }
            Token eqTok = p.consume();
            if (eqTok.type != TokType.EQ) {
                throw new SQLException("Expected '=' after column " + col);
            }
            ValueExpr rhs = p.parseValue();
            assignments.add(new java.util.AbstractMap.SimpleEntry<>(col, rhs));
            if (p.peek().type == TokType.COMMA) {
                p.consume();
            } else {
                break;
            }
        }

        Pred pred = row -> true;
        if (p.isKeyword("WHERE")) {
            p.consume();
            pred = p.parseOr();
        }
        if (p.peek().type != TokType.EOF) {
            throw new SQLException("Unexpected trailing SQL token: " + p.peek().text);
        }

        int updated = 0;
        for (Map<String, Object> row : rows) {
            if (pred.eval(row)) {
                for (Map.Entry<String, ValueExpr> entry : assignments) {
                    Object newVal = entry.getValue().eval(row);
                    row.put(entry.getKey(), newVal);
                }
                updated++;
            }
        }
        return updated;
    }
}
