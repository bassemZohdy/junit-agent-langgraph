package com.example;

public class StringValidator {
    
    public boolean isEmpty(String str) {
        return str == null || str.isEmpty();
    }
    
    public boolean hasLength(String str, int length) {
        return str != null && str.length() == length;
    }
    
    public boolean contains(String str, String substring) {
        return str != null && substring != null && str.contains(substring);
    }
    
    public boolean startsWith(String str, String prefix) {
        return str != null && prefix != null && str.startsWith(prefix);
    }
}
