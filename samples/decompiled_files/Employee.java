/*
 * Decompiled with CFR 0.152.
 */
public class Employee {
    private int id;
    private String name;
    private boolean isOld;
    private String dept;
    String query1 = "TRUNCATE TABLE users;";
    String query2 = "EXECUTE sp_update_user;";
    String query3 = "CALL sp_update_user();";
    String query4 = "DROP TABLE users;";
    String query5 = "CREATE TABLE users";

    public Employee(int id, String name, boolean isOld, String dept) {
        this.id = id;
        this.name = name;
        this.isOld = isOld;
        this.dept = dept;
    }

    public int getId() {
        return this.id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public String getName() {
        return this.name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public boolean isOld() {
        return this.isOld;
    }

    public void setOld(boolean old) {
        this.isOld = old;
    }

    public String getDept() {
        return this.dept;
    }

    public void setDept(String dept) {
        this.dept = dept;
    }
}
