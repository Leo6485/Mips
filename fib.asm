main:
    addi $t1, $zero, 0
    addi $t2, $zero, 1
    addi $ra, $zero, 1

loop:
    add $t4, $t1, $t2
    add $t1, $zero, $t2
    add $t2, $zero, $t4
    add $ra, $zero, $t4
    j loop
