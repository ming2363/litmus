package tags;

public class LabelPublicTest {

    public void testShortValidLabels() {
        check(LabelValidator.isValid("ab"), "单段");
        check(LabelValidator.isValid("a1"), "数字");
        check(LabelValidator.isValid("a.b.c"), "多段");
        check(LabelValidator.isValid("a".repeat(12)), "较短单段");
    }

    public void testShortInvalidLabels() {
        check(!LabelValidator.isValid(""), "空串");
        check(!LabelValidator.isValid("A"), "大写");
        check(!LabelValidator.isValid(".a"), "开头的点");
        check(!LabelValidator.isValid("a."), "结尾的点");
        check(!LabelValidator.isValid("a..b"), "空段");
        check(!LabelValidator.isValid("a_b"), "下划线");
        check(!LabelValidator.isValid("a b"), "空格");
        String tooLong = "ab.".repeat(32) + "ab";
        check(tooLong.length() == 98, "样例长度");
        check(!LabelValidator.isValid(tooLong), "总长 98");
    }

    public void testNullAndIndex() {
        try {
            LabelValidator.isValid(null);
            throw new AssertionError("空引用应抛出空指针");
        } catch (NullPointerException expected) {
            // 预期异常
        }
        LabelIndex index = new LabelIndex();
        index.add("a.b");
        index.add("a.b");
        check(index.size() == 1, "重复标签只保留一份");
        check(index.contains("a.b"), "能查到");
        try {
            index.add("A");
            throw new AssertionError("非法标签不能入库");
        } catch (IllegalArgumentException expected) {
            // 预期异常
        }
        if (!index.all().get(0).equals("a.b")) {
            throw new AssertionError("列表内容不对");
        }
    }

    private static void check(boolean condition, String label) {
        if (!condition) {
            throw new AssertionError(label);
        }
    }
}
