def program_reading(file):
    f = open(file)
    program = []
    for line in f:
        if line.find('new') != -1:
            program.append([line.split(' ')[1], 'new'])
            continue
        if line.find('.') != -1:
            program.append([line.split('.')[0], '.'])
            continue
        if line.find('null') != -1:
            program.append([line.split(' ')[0], 'null'])
            continue
        print("ERROR")
        f.close()
        return
    f.close()
    return program


def specification_computing(program):
    spec_post = []
    spec_pre = []
    for method in program:
        if method[1] == 'new':
            spec_pre.append([['emp']])
            spec_post.append([[method[0], '_']])
            continue
        if method[1] == '.':
            spec_pre.append([[method[0], '_']])
            spec_post.append([[method[0], 'val']])
            continue
        if method[1] == 'null':
            spec_pre.append([[method[0], 'val']])
            spec_post.append([['emp']])
            continue
    return spec_pre, spec_post


def forward_analysis(program):
    forward = []
    forward.append([['emp']])
    for method in program:
        if method[1] == 'new':
            if forward[-1] == [['emp']]:
                forward.append([[method[0], '_']])
                continue
            if forward[-1].count([method[0], '_']) != 0:
                temp = forward[-1].copy()
                forward.append(temp)
                continue
            if forward[-1].count([method[0], 'val']) != 0:
                temp = forward[-1].copy()
                ind = temp.index([method[0], 'val'])
                temp.remove([method[0], 'val'])
                temp.insert(ind, [method[0], '_'])
                forward.append(temp)
                continue
            else:
                temp = forward[-1].copy()
                temp.append([method[0], '_'])
                forward.append(temp)
                continue
        if method[1] == '.':
            if forward[-1] == [['emp']]:
                forward.append([[method[0], 'val']])
                continue
            if forward[-1].count([method[0], 'val']) != 0:
                temp = forward[-1].copy()
                forward.append(temp)
                continue
            if forward[-1].count([method[0], '_']) != 0:
                temp = forward[-1].copy()
                ind = temp.index([method[0], '_'])
                temp.remove([method[0], '_'])
                temp.insert(ind, [method[0], 'val'])
                forward.append(temp)
                continue
            else:
                temp = forward[-1].copy()
                temp.append([method[0], 'val'])
                forward.append(temp)
                continue
        if method[1] == 'null':
            if forward[-1] == [['emp']]:
                forward.append([['emp']])
                continue
            if forward[-1].count([method[0], 'val']) != 0:
                temp = forward[-1].copy()
                temp.remove([method[0], 'val'])
                if temp:
                    forward.append(temp)
                    continue
                else:
                    forward.append([['emp']])
                    continue
            if forward[-1].count([method[0], '_']) != 0:
                temp = forward[-1].copy()
                temp.remove([method[0], '_'])
                if temp:
                    forward.append(temp)
                    continue
                else:
                    forward.append([['emp']])
                    continue
            else:
                temp = forward[-1].copy()
                forward.append(temp)
                continue
    forward.pop()
    return forward


def backward_analysis(pre, post):
    backward = []
    backward.append(pre[-1])
    loc = len(pre)
    i = 1
    while i < loc:
        abduct = bi_abduction(post[-i-1], backward[0])[0]
        backward.insert(0, separating_conjunction(pre[-i-1], abduct))
        i += 1
    return backward


def bi_abduction(post, pre):
    post1_copy = post.copy()
    pre2_copy = pre.copy()
    if post1_copy == [['emp']]:
        abduct = pre2_copy
        frame = [['emp']]
        return abduct, frame
    if pre2_copy == [['emp']]:
        abduct = [['emp']]
        frame = post1_copy
        return abduct, frame
    for element in post1_copy:
        if pre2_copy.count(element) != 0:
            post1_copy.remove(element)
            pre2_copy.remove(element)
    for element_post in post1_copy:
        for element_pre in pre2_copy:
            if element_post[0] == element_pre[0]:
                if element_post[1] == 'val' and element_pre[1] == '_':
                    post1_copy.remove(element_post)
                    pre2_copy.remove(element_pre)
                if element_post[1] == '_' and element_pre[1] == 'val':
                    post1_copy.remove(element_post)
    if not pre2_copy:
        abduct = [['emp']]
    else:
        abduct = pre2_copy
    if not post1_copy:
        frame = [['emp']]
    else:
        frame = post1_copy
    return abduct, frame


def separating_conjunction(list1, list2):
    temp1 = list1.copy()
    temp2 = list2.copy()
    if temp1 == [['emp']]:
        return temp2
    if temp2 == [['emp']]:
        return temp1
    for element2 in temp2:
        for element1 in temp1:
            if element1[0] == element2[0]:
                if element1[1] != element2[1]:
                    element = [element1[0], 'val']
                    ind1 = temp1.index(element1)
                    ind2 = temp2.index(element2)
                    temp1.pop(ind1)
                    temp2.pop(ind2)
                    temp1.insert(ind1, element)
                    temp2.insert(ind2, element)
    for element2 in temp2:
        if temp1.count(element2) == 0:
            temp1.append(element2)
    return temp1


def frame_inference(list1, list2):
    leaks = []
    loc = len(list1)
    i = 0
    while i < loc:
        temp1 = list1[i].copy()
        temp2 = list2[i].copy()
        if temp1 == [['emp']]:
            leaks.append([['emp']])
            i += 1
            continue
        if temp2 == [['emp']]:
            leaks.append(temp1)
            i += 1
            continue
        temp = []
        for element1 in temp1:
            if element1 not in temp2:
                temp.append(element1)
        temp1 = temp
        for element1 in temp1:
            for element2 in temp2:
                if element1[0] == element2[0]:
                    temp1.remove(element1)
                    temp1.append([element2[0], '_'])
        if not temp1:
            leaks.append([['emp']])
        else:
            leaks.append(temp1)
        i += 1
    return leaks


def printing(list1):
    for element in list1:
        print(element)


file = 'program.java'
program = program_reading(file)
pre, post = specification_computing(program)
forward = forward_analysis(program)
backward = backward_analysis(pre, post)
leaks = frame_inference(forward, backward)
printing(leaks)
