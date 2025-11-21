# import sys
# n=int(input())
# arr=list(map(int,input().split()))
# #记录第一次出现的元素
# fl={}
# max_state=0
# for i in range(n):#i下标
#     if arr[i] in fl:
#        current=i-fl[arr[i]]-1
#        if current>max_state:
#            max_state=current
#     else:
#         fl[arr[i]]=i
# print(max_state)


# import sys
# n=int(input())
# card_list={}#字典，键值是花色，值是字典 
# for i in range(n):
#     card=input().split()
card =input().split()
suit=card[2]
num=int(card[1])
value=int(card[0])  
if suit not in card_list:
    card_list[suit]={}#如果字典里没有这个就新建花色
card_list[suit][value]=num#如果花色里没有这个牌就新建
total=0
for suit in card_list:
    sorted_sizes=sorted(card_list[suit].keys())
    m=len(sorted_sizes)
    if m<5:
        continue    
    for i in range(m-4):
        if sorted_sizes[i]+4==sorted_sizes[i+4]:
            mi=min(card_list[suit][size]for size in sorted_sizes[i:i+5])
            total+=mi#找到牌最小的数量
            for size in sorted_sizes[i:i+5]:
                card_list[suit][size]-=mi
    print(total)
  
#     suit=card[2]
#     num=int(card[1])
#     value=int(card[0])
#     if suit not in card_list:
#         card_list[suit]={}#如果字典里没有这个就新建花色

#     card_list[suit][value]=num#如果花色里没有这个牌就新建
# total=0

# for suit in card_list:
#     sorted_sizes=sorted(card_list[suit].keys())
#     m=len(sorted_sizes)
#     if m<5:
#         continue
#     for i in range(m-4):
#         if sorted_sizes[i]+4==sorted_sizes[i+4]:
#             mi=min( card_list[suit][size]for size in sorted_sizes[i:i+5])
#             total+=mi#找到牌最小的数量
#             for size in sorted_sizes[i:i+5]:
#                     card_list[suit][size]-=mi
# print(total)



# import sys
# n=int(input())
# arr=list(map(int,input().split()))
# fl={}
# for i in range(n):
#     if arr[i] in fl:
#         fl[arr[i]]+=1
#     else:
#         fl[arr[i]]=1
# sorted_fl=sorted(fl.values(),reverse=True)
# max_fl=sorted_fl[0]
# diff={}
# for key in fl:
#     diff[key]=max_fl-fl[key]
# sorted_diff=sorted(diff.values(),reverse=True)
# 2.
# 小红的项链
# 小红将n个珠子排成一排，然后将它们串起来，连接成了一串项链（连接后为一个环，即第一个和最后一个珠子也是相邻的），任意相邻两个珠子的距离为1。已知初始共有3个珠子是红色的，其余珠子是白色的。
# 小红拥有无穷的魔力，她可以对项链上的相邻两个珠子进行交换。小红希望用最小的交换次数，使得任意两个红色的珠子的最小距离不小于k，你能帮小红求出最小的交换次数吗？
import sys
n=int(input())
for i  in range(n):
    arr=list(map(int,input().split()))
    num=arr[0]
    k=arr[1]
    a1=arr[2]
    a2=arr[3]
    a3=arr[4]
    total=0
    if k<=num//3:
        sorted_arr=sorted([a1,a2,a3])
        if sorted_arr[1]-sorted_arr[0]>=k and sorted_arr[2]-sorted_arr[1]>=k and sorted_arr[2]-sorted_arr[0]>=k:
            total=0
        if sorted_arr[1]-sorted_arr[0]<k:
            total+=k-(sorted_arr[1]-sorted_arr[0])
        if sorted_arr[2]-sorted_arr[1]<k:
            total+=k-(sorted_arr[2]-sorted_arr[1])
        if num-sorted_arr[2]+sorted_arr[0]<k:
            total+=k-(num-sorted_arr[2]+sorted_arr[0])
        print(total)
    else:
        print(-1)
        