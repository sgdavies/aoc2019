
def verify (a,b,c,d,e,f):
    if not (a <= b <= c <= d <= e <= f):
        return False

    return a==b or b==c or c==d or d==e or e==f

def count_range (start_str, end_str, debug=False):
    a0,b0,c0,d0,e0,f0 = [int(x) for x in list(start_str)]
    ax,bx,cx,dx,ex,fx = [int(x) for x in list(end_str)]

    counter = 0

    for a in range(a0, ax+1):
      for b in range(a, 10):
        if a==a0 and b<b0:
            continue
        for c in range(b, 10):
          if a==a0 and b==b0 and c<c0:
              continue
          for d in range(c, 10):
            if a==a0 and b==b0 and c==c0 and d<d0:
                continue
            for e in range(d, 10):
              if a==a0 and b==b0 and c==c0 and d==d0 and e<e0:
                  continue
              for f in range(10):
                  if cmp([a,b,c,d,e,f],[ax,bx,cx,dx,ex,fx]) > 0:
                      print counter
                      return counter

                  if a==a0 and b==b0 and c==c0 and d==d0 and e==e0 and f<f0:
                      continue
                  if debug: print a,b,c,d,e,f,"==",verify(a,b,c,d,e,f)

                  if verify(a,b,c,d,e,f):
                      #print "Got one:",a,b,c,d,e,f
                      counter +=1


def tests ():
    assert(verify(1,1,1,1,1,1))
    assert(not verify(2,2,3,4,5,0))  # Don't test this
    assert(not verify(1,2,3,7,8,9))

    assert(count_range("123450", "123460", debug=True) == 1)
    assert(count_range("123400", "123500") == 11)

    print "All tests pass"

tests()

print count_range("165432","707912")
