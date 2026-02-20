package com.example.mod2;

public class Service2 {
    public String transform(String input) {
        if (input == null) {
            return "null";
        }
        return input.toUpperCase().trim();
    }
}
