package com.example.mod1;

import com.example.mod2.Service2;

public class Service1 {
    private Service2 service2;
    
    public Service1(Service2 service2) {
        this.service2 = service2;
    }
    
    public String process(String input) {
        return "Service1 processed: " + service2.transform(input);
    }
}
