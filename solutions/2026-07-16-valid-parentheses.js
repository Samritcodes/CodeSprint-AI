// Valid Parentheses (Easy)
// Tags: stack, string
// LeetCode: https://leetcode.com/problems/valid-parentheses/
//
// Given a string containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid (every open bracket is closed by the same type, in the correct order).
//
// Write your solution below. When you push this file (filled in),
// the Reviewer Agent will pick it up, generate the explanation +
// complexity write-up, and update the README automatically.

/**
 * @param {*} input
 * @return {*}
 */
// Valid Parentheses (Easy)
// Tags: stack, string
// LeetCode: https://leetcode.com/problems/valid-parentheses/
//
// Given a string containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid (every open bracket is closed by the same type, in the correct order).
//
// Write your solution below. When you push this file (filled in),
// the Reviewer Agent will pick it up, generate the explanation +
// complexity write-up, and update the README automatically.

/**
 * @param {*} input
 * @return {*}
 */
function solve(input) {
    const stack = [];
    const brackets = {
        '(': ')',
        '{': '}',
        '[': ']'
    };

    for (let char of input) {
        if (brackets[char]) {
            // If it's an opening bracket, push the corresponding closing bracket
            stack.push(brackets[char]);
        } else {
            // If it's a closing bracket, check if it matches the top of the stack
            if (stack.pop() !== char) return false;
        }
    }

    return stack.length === 0;
}