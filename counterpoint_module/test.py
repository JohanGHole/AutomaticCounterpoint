from music_module.constants import *
import copy

def print_all_sum_rec(target, current_sum, start, output, result):
 if current_sum == target:
   output.append(copy.copy(result))

 for i in range(start, target):
   temp_sum = current_sum + i
   if temp_sum <= target:
     result.append(i)
     print_all_sum_rec(target, temp_sum, i, output, result)
     result.pop()
   else:
     return

def print_all_sum(target):
 output = []
 result = []
 print_all_sum_rec(target, 0, 1, output, result)
 return output


n = 4
res = print_all_sum(n)
print(res)