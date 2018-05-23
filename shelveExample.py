# testing and learning shelve
import shelve
s = shelve.open("/home/pi/shelvesample")
s["name"]=["Chase", "Vince", "Fart"]
s["ability"] = ["Code", "Market", "Stink"]
s.close()

a = shelve.open("/home/pi/shelvesample.dat")
print (a["name"])
print (a["ability"])
a.close()