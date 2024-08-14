//Name: Suresh Mudavath
//Id: 1002079147

package org.example;

import static org.junit.Assert.*;
import org.junit.Before;
import org.junit.Test;
import java.io.ByteArrayOutputStream;
import java.io.PrintStream;

public class MyStackTest {
    private MyStack stack;
    @Before
    public void setUp() {
        // Before every test, create a new instance of the stack.
        stack = new MyStack();
    }

    // confirms that the stack is empty at first.
    @Test
    public void testEmptyStack() {
        assertTrue(stack.empty());
    }

    // tests where an element is pushed into the stack and then a peek is taken to see if the top element is expected.
    @Test
    public void testPushAndPeek() {
        stack.push(1);
        assertEquals(1, stack.peek());
        assertFalse(stack.empty());
    }

    // Tests whether the stack becomes empty by pushing an element and then popping it.
    @Test
    public void testPushAndPop() {
        stack.push(1);
        assertEquals(1, stack.pop());
        assertTrue(stack.empty());
    }

    // Tests pushing multiple elements and then popping them to check the order and emptiness of the stack.
    @Test
    public void testPushMultiple() {
        stack.push(1);
        stack.push(2);
        stack.push(3);
        assertEquals(3, stack.pop());
        assertEquals(2, stack.pop());
        assertEquals(1, stack.pop());
        assertTrue(stack.empty());
    }

    // checks that the 'print' method prints the stack elements correctly.
    @Test
    public void testPrint() {
        stack.push(1);
        stack.push(2);
        stack.push(3);
        stack.push(4);

        // In order to obtain printed content, redirect standard output.
        ByteArrayOutputStream outContent = new ByteArrayOutputStream();
        System.setOut(new PrintStream(outContent));

        stack.print();

        String expectedOutput = "4\n3\n2\n1\n";
        // Verify if the printed content matches the expected output
        assertEquals(expectedOutput, outContent.toString().replaceAll("\r", ""));
    }

    // Cause-Effect Test
    //Check the top element and emptiness after pushing two elements and popping one.
    @Test
    public void testCauseEffectPushPop() {
        stack.push(1);
        stack.push(2);
        stack.pop();
        assertEquals(1, stack.peek());
        assertFalse(stack.empty());
    }

    // Equivalence Partitioning Test
    // Push a string and verify if it can be peeked
    @Test
    public void testPushString() {
        stack.push("Hello");
        assertEquals("Hello", stack.peek());
    }

    // Equivalence Partitioning Test
    // Push a null element and verify if it can be peeked as null
    @Test
    public void testPushNull() {
        stack.push(null);
        assertNull(stack.peek());
    }

    // Boundary Value Test
    // Attempt to push beyond the stack's capacity
    @Test
    public void testPushToMaxCapacity() {
        stack.push(1);
        stack.push(2);
        stack.push(3);
        // Verify if the stack is already full and that adding new elements is not allowed.
        try {
            stack.push(4);
        } catch (IllegalStateException e) {
        }
    }
    // Verify the behavior when the stack is at its maximum capacity
    @Test
    public void testStackAtMaxCapacity() {
        stack.push(1);
        stack.push(2);
        stack.push(3);
        assertFalse(stack.empty());
        assertEquals(3, stack.pop());
        assertEquals(2, stack.pop());
        assertEquals(1, stack.pop());
        assertTrue(stack.empty());
    }
}
