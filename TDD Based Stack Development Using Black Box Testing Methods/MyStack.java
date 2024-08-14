//Name: Suresh Mudavath
//Id: 1002079147
package org.example;

import java.util.ArrayList;
import java.util.List;
public class MyStack {
    public List<Object> stack;
    public MyStack() {
        stack = new ArrayList<>();
    }
    public boolean empty() {
        return stack.isEmpty();
    }
    public Object peek() {
        return stack.get(stack.size() - 1);
    }
    public Object pop() {
        return stack.remove(stack.size() - 1);
    }
    public void push(Object item) {
        stack.add(item);
    }
    public void print() {
        for (int i = stack.size() - 1; i >= 0; i--) {
            System.out.println(stack.get(i));
        }
    }

}

