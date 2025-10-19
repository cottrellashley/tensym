.PROGRAM v1
.BUFFERS a,b,c,d,e
.SCALARS x

.FUNC F(u, v)
  ADD   r1, u, v
  DERIV r0, r1, x
  RET   r0
.END

.BLOCK 1 TARGET e[0,0,0,0]
  LDELEM r1, a, 0, 0, 0, 0
  LDELEM r2, b, 1, 0, 0, 1
  LDELEM r3, c, 0, 0, 1, 1
  MUL    r4, r2, r3
  ADD    r5, r1, r4
  LDELEM r6, d, 0, 0, 0, 0
  SUB    r7, r5, r6
  STORE  e, 0, 0, 0, 0, r7
.END

.BLOCK 2 TARGET e[1,1,1,1]
  LDELEM r1, a, 1, 1, 1, 1
  LDELEM r2, b, 1, 1, 1, 1
  CONST  r3, 2
  MUL    r4, r3, r2
  ADD    r5, r1, r4
  LDELEM r6, c, 1, 1, 1, 1
  ADD    r7, r5, r6
  STORE  e, 1, 1, 1, 1, r7
.END

.BLOCK 3 TARGET e[2,0,2,0]
  LDELEM r1, b, 2, 0, 2, 0
  LDELEM r2, c, 2, 0, 2, 0
  LDELEM r3, d, 2, 0, 2, 0
  SUB    r4, r2, r3
  MUL    r5, r1, r4
  STORE  e, 2, 0, 2, 0, r5
.END

.BLOCK 4 TARGET e[3,3,0,0]
  LDELEM r1, d, 0, 3, 0, 3
  LDELEM r2, a, 0, 0, 3, 3
  LDELEM r3, a, 3, 3, 0, 0
  SUB    r4, r2, r3
  CALL   r5, F, r1, r4
  STORE  e, 3, 3, 0, 0, r5
.END
