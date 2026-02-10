print("1. MONDAY \n", "2.TUESDAY \n" ,"3.WEDNESDAY \n","4.THURSDAY\n","5.FRIDAY\n" ,"6.SATURDAY\n","7.SUNDAY\n")
print("Any one of choice above/n")
choice=int(input("enter  the choice:  "))
match choice: 
 case 1:
     print("TODAY IS  :  MONDAY")
 case 2:
     print("TODAY IS  : TUESDAY")
 case 3:
     print("TODAY IS  : WEDNESDAY")
 case 4:
     print("TODAY IS  : THURSDAY")
 case 5: 
     print("TODAY IS  :  FRIDAY") 
 case 6:    
     print("TODAY IS  :  SATURDAY")
 case 7: 
     print("TODAY IS   :  SUNDAY")  
 case _:
     print("GIVE    THE   VALID  INPUT")
