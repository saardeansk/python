                   swaping logic  using  XOR  (or)  sum logic
             ( XOR )
   a=a^b
   b=a^b
   a=a^b
example
a=5,b=10
 0101
 1010
 1111
a=15
  1111
  1010
  0101
b=5
  1111
  0101
  1010
a=10
  (SUM LOGIC)
 SUM=a+b
a=sum-a
b=sum-b
  swapped
                                   example program in python
   n=int(input("enter the number of times to swap the variable : "))
for i in range(n):
    a=int(input("enter the value of a : "))
    b=int(input("enter the value of b : "))
    sm=a+b
    if(a==0 and b==0):
       print("give the value it becomes only zero")
       continue
    if(a==b):
       print ("both the a and  b are same value")
       continue
    if(a==0 or b==0 or a!=0 or b!=0):
        print("the value of a and b: ",a,b)
        a=sm-a
        b=sm-b
        print("the swapped value is ",a,b)
       
