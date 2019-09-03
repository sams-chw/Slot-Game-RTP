from itertools import combinations, combinations_with_replacement, permutations
import numpy as np

def combine_symbol(hits, hits_total, pay_table, symbol, reel_count=5):
    reel = []
    for col in pay_table.columns:
        if pay_table.loc[symbol, col] > 0:
            reel.append(col)
    sym_count = len(reel)

    prod_lst = []

    for i in range(sym_count):
        product = 1
        for j in range(reel_count - i):
            product *= hits.loc[symbol, list(hits.columns)[j]] + hits.loc['wild', list(hits.columns)[j]]
        for k in range(i):
            if k == 0:
                product *= (hits_total[reel_count - i] 
                            - (hits.loc[symbol, list(hits.columns)[reel_count - i]] 
                            + hits.loc['wild', list(hits.columns)[reel_count - i]]))
            else:
                product *= (hits_total[reel_count - k])

        prod_lst.append(product)

    return prod_lst

def combine_scatter(lst1, lst2):
    result={}
    current = 0
    for locations in combinations(range(len(lst1) + len(lst2)), len(lst2)):
        tmp = lst1[:]
        for locations, element in zip(locations, lst2):
            tmp.insert(locations, element)
        result[current] = tmp
        current += 1
    return result

def product_scatter(df, df_total, sym_count, reel_count=5):
    lst1 = ['scatter']*sym_count
    lst2 = ['~scatter']*(reel_count-sym_count)
    combined = combine_scatter(lst1, lst2)
    if sym_count == 3:
        print("An example of hits for any 3 'scatter' symbols:")
        print()
        for item in combined.values():
            print(item)
    sum_product = []
    for key in combined.keys():
        product = 1
        for count, element in enumerate(combined[key]):
            if element in lst1:
                product *= (df.iloc[1, count]*3)
            else:
                product *= (df_total[count] - 3*df.iloc[1, count])
        sum_product.append(product)
    return np.sum(sum_product)

def combine_chip(target_sum=6):
    a = [3,2,1,0,0]
    arr = []
    combo = []    

    for r in range(0, len(a)+1):        
        arr += list(combinations_with_replacement(a, r))

    for item in arr:        
        if sum(item) == target_sum:
            combo.append(item)

    chip_combo = []
    for item in combo:
        if len(item) == 5:
            if item not in chip_combo:
                chip_combo.append(item)

    chip_hits = []
    for item in chip_combo: 
        chip_hits_temp=[]
        for perm in list(permutations(item)):
            if perm not in chip_hits_temp:
                chip_hits_temp.append(perm)
        chip_hits.extend(chip_hits_temp)

    return chip_hits, len(chip_hits)

def denominator(df_total, times):
    multiply = 1
    for i in range(times):
        multiply *= (df_total-i)
    return multiply

def numerator(chip, times):
    multiply = 1
    for k in range(times):
        multiply *= ((chip-k)*(3-k))
    return multiply


def chip_prob_dist(df, df_total, chip_count=6, reel_count=5):
    chip_prob_table={}
    chip_hits_table, chip_hits_length = combine_chip(chip_count)
    for i in range(chip_hits_length):
        chip_prob=[]
        for j in range(reel_count):
            if chip_hits_table[i][j] == 0:
                temp = (df_total[j] - 3*df.loc['chip'][j])/df_total[j]
            else:
                temp = np.divide(numerator(df.loc['chip'][j], chip_hits_table[i][j]),
                                    denominator(df_total[j], chip_hits_table[i][j]))
            chip_prob.append(temp)
        chip_prob_table[i]= chip_prob
    return chip_prob_table

def chip_prob_dist_combined(df, df_total, occurance, reel_count=5):
    chip_prob_table = chip_prob_dist(df, df_total, occurance)
    chip_prob_combined={}
    for key in chip_prob_table.keys():
        product=1
        for i in range(reel_count):
            product *= chip_prob_table[key][i]
        chip_prob_combined[key] = product
    return chip_prob_combined

def combine_coin_values(df_chip, count):
    df_chip_ix = list(combinations_with_replacement(list(df_chip.index), count))
    df_chip_ix_combo={}
    for i in range(len(df_chip_ix)):
        list_temp=[]
        for item in list(permutations(df_chip_ix[i])):
            if item not in list_temp:
                list_temp.append(item)
        df_chip_ix_combo[i]=list_temp
    return df_chip_ix_combo, df_chip_ix

def chip_payout_per_count(df_chip, df_chip_total, count):
    df_chip_ix_combo, df_chip_ix = combine_coin_values(df_chip, count)
    chip_value_prob_dist={}

    for key,value in df_chip_ix_combo.items():
        combo_key = df_chip_ix[key]
        combo_sum=0
        for combo in value:
            product=1
            for count, k in enumerate(combo):
                product *= np.divide((df_chip.loc[k, 'Reel1']-count),
                                    (df_chip_total[0]-count))
            combo_sum += product/len(value)
        chip_value_prob_dist[combo_key] = combo_sum  
    chip_value_prob = 0
    chip_value_payout = 0
    for key, value in chip_value_prob_dist.items():
        sum_temp_payout=0
        for i in key:
            sum_temp_payout += int(i)
        chip_value_payout += sum_temp_payout*value 
        chip_value_prob += value
    return chip_value_payout

def chip_payout_combined(df_chip, df_chip_total, chip_prob_combined, occurance, reel_count=5):
    chip_hits_table, chip_hits_length = combine_chip(occurance)
    pay_count_prob=[]
    for key, value in chip_prob_combined.items():
        pay_count=0
        for col in range(reel_count):
            count = chip_hits_table[key][col]
            pay_count += chip_payout_per_count(df_chip, df_chip_total, count)
        if occurance == 15:
            pay_count_prob.append(pay_count*value*250000)       #Jackpot
        else:
            pay_count_prob.append(pay_count*value)
    return np.sum(pay_count_prob)
