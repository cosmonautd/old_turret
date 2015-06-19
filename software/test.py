import save, time, datetime
s = save.Drive("", "")
now = datetime.datetime.now()
l = s.get_link(now)
print l
type(l)

