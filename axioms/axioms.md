ArrayList
=========
* `get(list()) == ERROR //not sure how best to represent this but it is the base case for next 2`
* `get(set!(a, i, e), j) == ITE(i == j, e, get(a, j))`
* `get(add!(a, e), i) == ITE(size(a) == i-1, e, get(a, i))`
* `size(list()) == 0`
* `size(add!(a, e)) == size(a) + 1`
* `size(set!(a, i, e)) == size(a)`

File
======
* `read(filereader(file(f, d, l, n), p)) == d[p]`
* `read!(filereader(file(f, d, l, n), p)) == filereader(file(f, d, l, n), p+1)`
* `ready(filereader(file(f, d, l, n), p)) == ITE(p != l-1, True, False)`

HashMap
=======

* `put!(put!(h, k1, v1), k2, v2) == ITE(k2.equals(k1), put!(h, k2, v2), put!(put!(h, k2, v2), k1, v1))`
* `put(put!(h, k1, v1), k2, v2) == ITE(k2.equals(k1), v1, put(h, k2, v2))`
* `put([], k, v) == null`
* `get(put!(h, k1, v), k2) == ITE(k2.equals(k1), v, get(h, k2))`
* `get([], k2) == null`
* `remove!(put!(h, k1, v), k2) == ITE(k2.equals(k1), h, put!(remove!(h, k2), k1, v))`
* `remove!([], k) == []`
* `remove(put!(h, k1, v), k2) == ITE(k2.equals(k1), v, remove(h, k2))`
* `remove([], k) == null`
* `containsKey(put!(h, k1, v), k2) == ITE(k2.equals(k1), True, containsKey(h, k2))`
* `containsKey([], k) == False`
* `containsValue(put!(h, k, v1), v2) == ITE(v2.equals(v1), True, containsValue(h, v2))`
* `size(put!(h, _, _)) == size(h) + 1`
* `size([]) == 0`

HashSet
=======

* `add!(add!(s, e1), e2) == ITE(e2.equals(e1), add!(s, e1), add!(add!(s, e2), e1))`
* `add(add!(s, e1), e2) == ITE(e2.equals(e1), False, add(s, e2))`
* `add([], e) == True`
* `remove!(add!(s, e1), e2) == ITE(e2.equals(e1), s, add!(remove!(s, e2), e1))`
* `remove!([], e) == []`
* `remove(add(s, e1), e2) == ITE(e2.equals(e1), True, remove(s, e2))`
* `remove([], e) == False`
* `size(add(s, _)) == size(s) + 1`
* `size([]) == 0`

TreeSet
=======

* `add!(add!(s, e1), e2) == ITE(e2.equals(e1), add!(s, e1), add!(add!(s, e2), e1))`
* `clear!(_) == []`
* `add(add!(s, e1), e2) == ITE(e2.equals(e1), False, add(s, e2))`
* `add([], e) == True`
* `contains(add!(s, e1), e2) == ITE(e2.equals(e1), True, contains(s, e2))`

ArrayDeque
==========

* `removeFirst!(addFirst!(d, e)) == d`
* `removeFirst!(addLast!(d, e)) == ITE(size(d)==0, [], addLast!(removeFirst!(d), e))`
* `removeFirst!([]) == []`
* `removeFirst(addFirst!(d, e)) == e`
* `removeFirst(addLast!(d, e)) == ITE(size(d)==0, e, removeFirst(d))`
* `removeFirst([]) == null // Note: In Java this is an exception`
* `removeLast!(addLast!(d, e)) == d`
* `removeLast!(addFirst!(d, e)) == ITE(size(d)==0, [], addFirst!(removeLast!(d), e))`
* `removeLast!([]) == []`
* `removeLast(addLast!(d, e)) == e`
* `removeLast(addFirst!(d, e)) == ITE(size(d)==0, e, removeLast(d))`
* `removeLast([]) == null // Note: In Java this is an exception`
* `peekFirst(addFirst!(d, e)) == e`
* `peekFirst(addLast!(d, e)) == ITE(size(d)==0, e, peekFirst(d))`
* `peekLast(addLast!(d, e)) == e`
* `peekLast(addFirst!(d, e)) == ITE(size(d)==0, e, peekLast(d))`
* `size(addFirst!(d, e)) == size(d) + 1`
* `size(addLast!(d, e)) == size(d) + 1`
* `size([]) == 0`
* `isEmpty(s) == ITE(size(s)==0, True, False)`

DES Example (private key -- symmetric crypto)
===========

* `let g = getInstance("DES/ECB/PKCS5Padding") in` <br />
  ` let t = doFinal(init(g, "Cipher.ENCRYPT_MODE", k1), t1) in` <br /> 
   `doFinal(init(g,"Cipher.DECRYPT_MODE", k2), t) == ITE(k2.equals(k1), t1, GARBAGE)`

RSA Example (public key -- asymmetric crypto)
=========== 

* `let g = getInstance("RSA/ECB/PKCS1Padding") in` <br />
  `let t = doFinal(init(g, "Cipher.ENCRYPT_MODE", getPublic(k1)), t1) in` <br />
   `doFinal(init(g,"Cipher.DECRYPT_MODE", getPrivate(k2)), t) == ITE(k2.equals(k1), t1, GARBAGE)`