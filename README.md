# SudoLang
## A language for absolute beginners

Sudo is a language based off pseudocode, to help enforce basic programming concepts like assignment, conditionals, and repetition.

The language is structured off a [simple language](https://augustine.myusa.cloud/perugini/AveMaria/teaching/courses/csci151/LectureNotes/pseudocodeLanguage.html) designed by [Dr. Saverio Perugini](https://saverio.carrd.co/) to teach these concepts to introductory students.


The reader may well say, "Just use Python, bro?"

Well, bro, there a number of reasons why a student's learning experience could be tainted by a language like Python. The primary reason is that Python is a "hodgepodge of a language" and tries to be too many things at once. Students often will miss the entire point of an assignment designed to help them think algorithmically, focusing instead on some shiny and obscure "syntactic sugar", of which Python is chock-full. For instance, Sudo limits arithmetic operations to those between the same type, avoiding weird expressions like `"Hello" * 100` (This excludes of course floats and ints).

Sudo removes this dangerous pitfall by providing a language stripped of any juicy language features, leaving a simple set of instructions to help new students formulate their ideas in to mechanical procedures.

# Basic Syntax

If you're already familar with programming, you might find Sudo mildly infuriating. There are no loops, no functions, and only primitive data types. The whole language can be broken down into five basic rules.

## 1. Let Statements

The Let Statement allows you to assign the output of an expression to a particular mneumonic representation. 


Syntax -> `let <mneumonic> be <expression>`

Examples:

```
let x be 5
let interest_rate be 0.14
let x be x + 1
let ratio be (x + 5 / interest_rate)

return ratio
```

## 2. If Statements

The If Statement allows you to conditionally execute a line of code. The body of the statement will only execute if the expression evaluates to True.


Syntax -> `if <comparison expression>, then <statement(s)>`

Examples:

```
let a be 1

if a + 6 > 7, then
    let limit be "not too far"

if a - 6 <= 7, then let limit be 2.17

return limit
```

## 3. If-Else Statements

The If-Else Statement simply provides alternative execution case for when the condition from an If statement evaluates False. 


Syntax -> `If <comparison expression>, then <statements(s)> else <statement(s)>`

Examples:
```
let a be "not too far"
let speed be 60
let score be 73

if limit != "not too far", then
    if speed == 60, then
        let score be 7009.56
else
    let answer be score - 75

return score
```


## 4. Return Statement

Return statements are used to simply return the value of a statement or expression and terminate the evalutation. Return statements cannot be null, you must return something.


Syntax -> `return <mneumonic>`

Examples:
```
let wrong be 3
let right be 7

if wrong + wrong == right, then 
    return True
else
    return False

return "this will never execute"
```

## 5. Goto and Marker Statements

Goto Statements allow for continuous loops of instructions demarcated by Marker Statements.

Marker Syntax -> `@ <digit>`

Goto Syntax -> `goto instruction <digit>`

Examples:

```
let n be 5
let result be 1
@ 1
if n > 0, then
   let result be result * n
   let n be n - 1
   goto instruction 1
return result
```

Here's one that's a little more complex:
```
let maxPrimes be 20
let primesSeen be 0
let n be 2  # Start with the first prime

@1 # Main Loop
if primesSeen < maxPrimes, then
   let isPrime be True
   let x be 2
   
   @1.1 # Divisor check loop
   if x * x <= n, then
      if isPrime == True, then  # Separate the AND into nested if
         let temp be 0
         let quotient be 0
         
         @1.2 # Division calculation loop
         if temp + x <= n, then
            let temp be temp + x
            let quotient be quotient + 1
            goto instruction 1.2
         
         let divisible be quotient * x
         if divisible == n, then
            let isPrime be False
            goto instruction 1.3  # Skip to after divisor checks
         
         let x be x + 1
         goto instruction 1.1
      goto instruction 1.1  # If not prime anymore, keep checking until x*x > n
   
   @1.3  # After divisor checks
   if isPrime == True, then
      print n
      let primesSeen be primesSeen + 1
   
   if n == 2, then
      let n be 3  # After checking 2, skip to 3
   else
      let n be n + 2  # Skip even numbers
   
   goto instruction 1
```

## Additional Syntax

As demonstrated in the previous example, variables and expressions can be printed to the screen using 
`print <expression>`, which simple displays the value without terminating the program. 

Unlike `return`, `print` statements can be null, which print a new line.


Additionally, comments, can be written using the `#` symbol.

# Using SudoLang

The interpreter gives user the ability to interact with a sudolang program live in an "interactive" mode, as well as regular execution of a script. 

Pass a file to the interpreter using `./main file.sudo` 


To remain in interactive mode, add the `-i` flag -> `./main -i file.sudo`
