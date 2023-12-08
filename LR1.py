from prettytable import PrettyTable
import pandas as pd
import pickle
import os

grammar = []
terminal = []
non_terminal = []
filename = 'input/4/4_'

def pickle_store(data, save_path):
    with open(save_path + '.pickle', 'wb') as f:
        pickle.dump(data, f)

def find_next_ele_by_point(stringin):
    idx = stringin.find('.')
    ele = ''
    for i in range(1,3):
        ele += stringin[idx + i]
        if ele in terminal + non_terminal:
            break
    
    return ele

def find_end_ele(stringin):
    ele = ''
    for i in range(len(stringin) - 1, -1, -1):
        ele = stringin[i] + ele
        if ele in terminal + non_terminal:
            break
    return ele

def find_first_ele(stringin):
    ele = ''
    for i in range(len(stringin)):
        if stringin[i] == '.':
            continue
        ele += stringin[i]
        if ele in terminal + non_terminal:
            break
    return ele

def find_after_point(stringin, target):
    if stringin.find('.') != len(stringin) - 1 and find_next_ele_by_point(stringin) == target:
        return True
    else:
        return False

def find_after_point_all(arr, target):
    output = []
    for i in arr:
        if find_after_point(i[0], target):
            output.append(i)
    return output

def find_next_ele(target, stringin):
    to_find = stringin[0].split('.')[1]
    target_idx = to_find.find(target)
    if (target_idx + len(target) > len(to_find) - 1):
        return -1
    elif target_idx == -1:
        return -2
    else:
        ele = ''
        for i in range(target_idx + len(target), len(to_find)):
            ele += to_find[i]
            if ele in terminal + non_terminal:
                break
        return ele

def FIRST(target, gr):
    output = []
    for i in gr:
        if find_first_ele(i) == target:
            temp = find_first_ele(i.split('->')[1])
            if temp in terminal:
                output.append(temp)
            elif temp in non_terminal:
                output.append(FIRST(temp, gr))

    return output

def FOLLOW(target, clo, st):
    output = []

    next = find_next_ele(target, st)
    if next == -1:
        output += st[1]
    if next in terminal:
        output.append(next)
    elif next in non_terminal:
        ele = FIRST(next, grammar)
        output += ele
    return output


def call_all_closure(target, g):
    count = 0
    output = []
    output.append(target)

    while(True):
        temp = output[count][0].split('->')
        item = temp[1]
        if item.find('.') != len(item) - 1:
            item = find_next_ele_by_point(item)
            if(g.get(item, 0) != 0):
                for i in g[item]:
                    lookahead_item = FOLLOW(item, output, output[count])
                    if item + '->.' + i not in [t[0] for t in output]:                        
                        output.append([item + '->.' + i, lookahead_item])
                    else:
                        idx = [t[0] for t in output].index(item + '->.' + i)
                        output[idx][1] = list(set(output[idx][1]).union(set(lookahead_item)))


        count += 1

        if len(output) <= count:
            break
    return output

def grammar_to_dict(grammar):
    gr_dict = {}
    for x in grammar:
        g = x.split('->')
        if gr_dict.get(g[0], 1000) == 1000:
            gr_dict[g[0]] = []
        gr_dict[g[0]].append(g[1])
    return gr_dict

def move_point(x):
    token = find_next_ele_by_point(x)
    pos = x.find('.')
    x = list(x)
    temp = x[pos]
    x[pos:pos + len(token)] = token    
    x[pos + len(token)] = temp
    
    return "".join(x)

count = 0
with open(filename + 'grammar.txt', 'r') as f:
    for i in f.readlines():
        if count == 0:
            temp1 = i.strip().split(': ')
            temp2 = temp1[-1].split(', ')
            terminal = temp2
        elif count == 1:
            temp1 = i.strip().split(': ')
            temp2 = temp1[-1].split(', ')
            non_terminal = temp2
        else:
            temp = i.strip()
            if temp.find('|'):
                A = temp.split('->')
                L = A[0]
                R = A[1].split('|')
                for x in R:
                    grammar.append(L + '->' + x)
            else:
                grammar.append(i.strip())
        count += 1

grammar.insert(0, grammar[0][0] + '\'->.' + grammar[0][0])
grammar_dict = grammar_to_dict(grammar)
print(grammar)
print(grammar_dict)
state = []
state.append(call_all_closure([grammar[0], ['$']], grammar_dict))

parsing_table = []

for st in state:
    st_temp = st.copy()
    while (len(st_temp) > 0):
        dec = st_temp[0]
        st_temp.remove(dec)
        eat_list = []
        action = []
        action.append(state.index(st))
        if dec[0].find('.') != len(dec[0]) - 1:
            eat = find_next_ele_by_point(dec[0])
            action.append(eat)
            eat_list = find_after_point_all(st_temp, eat)

            for i in eat_list:
                st_temp.remove(i)

            eat_list.insert(0, dec)
            # eat_list.append(dec)
            # eat_list.sort()
            all_closure_temp = []

            for i in eat_list:
                x = i.copy()
                x[0] = move_point(i[0])
                all_closure_temp += call_all_closure(x, grammar_dict)
            
            if all_closure_temp not in state:
                state.append(all_closure_temp)
                action.append(len(state) - 1)
            else:
                action.append(state.index(all_closure_temp))
            parsing_table.append(action)


################# print all statement #################
print('/////////////////// state ///////////////////')
for i in range(len(state)):
    print(i, ':', state[i])
print('/////////////////// parsing table ///////////////////')
################# create parsing table #################
return_table = []
for i in range(len(state)):
    if i == 1:
        continue
    return_bool = False
    return_temp = ''
    return_lookahead = ''
    for j in state[i]:
        if j[0][-1] == '.':
            return_bool = True
            return_temp = j[0]
            return_lookahead = j[1]
            break

    if return_bool:
        return_temp = return_temp[0:-1]
        if return_temp in grammar:
            idx = grammar.index(return_temp)
            for x in return_lookahead:
                return_table.append([i, x, 'r' + str(idx)])

table = []
col = ['$'] + terminal + non_terminal
terminal_size = len(col)
table_temp = []
for i in range(terminal_size):
    table_temp.append('')
for i in range(len(state)):
    table.append(table_temp)

df = pd.DataFrame(table, columns=col)
df.at[1, '$'] = 'Acc'
for i in parsing_table:
    if i[1] in terminal:
        df.at[i[0], i[1]] = 's' + str(i[2])
    else:
        df.at[i[0], i[1]] = i[2]

for i in return_table:
    df.at[i[0], i[1]] = i[2]

# print(df)

table = df.values

PT = PrettyTable()
PT.field_names = [''] + col
for i in range(len(table)):
    temp = table[i].tolist()
    PT.add_row([i] + temp)

print(PT)

if not os.path.isdir('tables'):
    os.mkdir('tables')

pickle_store(df, 'tables/complete_table')
pickle_store(grammar, 'tables/grammar')
pickle_store(filename, 'tables/filename')
pickle_store(terminal, 'tables/terminal')


print('\n\n/////////////////// Start Parsing ///////////////////')
os.system("python LR1_parse.py")