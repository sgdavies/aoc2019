DEBUG=False
import time, sys

PATTERNS = { 0: [0,1,0,-1]}
def get_pattern(ix, desired_length):
    if (ix,desired_length) in PATTERNS:
        return PATTERNS[(ix,desired_length)]

    if ix in PATTERNS:
        source = PATTERNS[ix]
    else:
        source = []
        for item in PATTERNS[0]:
            for repeat in range(ix+1):  # 0th one has 1 of each
                source.append(item)

        PATTERNS[ix] = source

    pattern = list(source)
    while len(pattern) < desired_length + 1:
        pattern += list(source)

    pattern = pattern[1:desired_length+1]  # left shift
    PATTERNS[(ix,desired_length)] = pattern

    return pattern

def fft(input_signal, phases, start_position=0, length=8):
    signal = [int(c) for c in input_signal]

    for phase in range(phases):
        next_signal = ""

        # For 1,2,3,4:
        #    1*
        for ix in range(len(signal)):
            out_digit = str(sum([a*b for a,b in zip(signal, get_pattern(ix, len(signal)))]))[-1]
            next_signal += out_digit

        # if DEBUG: print(next_signal[:50], "...", next_signal[-50:])
        signal = [int(c) for c in next_signal]

    return next_signal[start_position:start_position+length]

def fft_fast(input_signal, phases, start_position=0, length=8, all=False):
    # Not O(N^2)
    # Use patterns in output to generate next signal quickly
    # E.g. signal length 10.
    # - "Lx" = "sum of last x digits"
    # - ^=1, v=-1
    # ^0v0^0v0^0 L10-L9 -L8 +L7 +L6 -L5 -L4 +L3 +L2 -L1
    # 0^^00vv00^ L9 -L7 -L5 +L3 +L1
    # 00^^^000vv L8 -L5 -L2
    # 000^^^^000 L7 -L3
    # 0000^^^^^0 L6 -L1
    # 00000^^^^^ L5
    # 000000^^^^ L4
    # 0000000^^^ L3
    # 00000000^^ L2
    # 000000000^ L1
    #
    # So algo is:
    # start on final digit. Keep running sum of final N digits. Run through half the array doing this and adding to next signal.
    # after N/2: diff = N/2, sigX = Lx -L(x-diff)
    # row=1:N
    # Lr = L(N-row+1)
    # nextL = Lr - r (-r, -r, etc) giving Ls - e.g.           Ls = [5] or [8,5,2] or [9,7,5,3,1]
    # Factors = [+,-,-,+] etc - i.e. [1,-1,-1,1][Ls-index %4] so   [1]   [1,-1,-1]  [1,-1,-1,1,1]
    # Then zip/multiply and sum together
    #
    # Importantly, note that next_sig[Xn] only depends on sig[Xn, Xn+1, etc] - it never depends on smaller n
    # So we don't need to bother calculating any next_sig values for n<start_position - just leave blank.
    #
    # import pdb; pdb.set_trace()
    N = len(input_signal)
    cap = N+1 - start_position
    wave = []
    while len(wave) < N:
        wave += [1,-1,-1,1]

    signal = [int(c) for c in input_signal]

    for phase in range(phases):
        # E.g. one phase of "12345678" gives "48226158"
        next_signal = [None]*N
        sumLs = {}
        sumL = 0
        for ix in range(1, cap):
            sigix = N-ix  # Row index from the top, starting on 0
            rowix = sigix+1 # Row index from top, starting on 1
            sumL += signal[sigix]
            sumLs[ix] = sumL
            ls = []
            lix = ix
            while True:
                ls.append(sumLs[lix])
                lix -= rowix
                if lix <= 0:
                    break
            combo = list(zip(ls, wave))
            total = sum([a*b for a,b in combo])
            next_signal[sigix] = int(str(total)[-1])

        signal = next_signal

    if all:
        return "".join([str(x) for x in next_signal])
    else:
        return "".join([str(x) for x in next_signal[start_position:start_position+length]])


def longer_fft(input_signal, repeats, phases):
    output_position = int(input_signal[:7])
    input_signal_long = input_signal*repeats

    output_signal = fft_fast(input_signal_long, phases, all=True)
    #return output_signal[output_position:output_position+1]
    print("Input signal: {}\nRepeated {} times\tLooking for output at index {}".format(input_signal, repeats, output_position))
    out = output_signal[output_position:output_position+8]
    print("Output: {}".format(out))
    # import pdb; pdb.set_trace()
    return out

def test(input_signal, phases, expected):
    start = time.time()
    output_fft = fft(input_signal, phases, length=len(expected))
    t1 = time.time() - start
    start = time.time()
    output_fft_fast = fft_fast(input_signal, phases, length=len(expected))
    t2 = time.time() - start
    if DEBUG: print("Expected: {}, got:\n{} ({:.2f}s) from fft\n{} ({:.2f}s) from fft_fast".format(expected, output_fft, t1, output_fft_fast, t2))
    assert(output_fft == expected)
    assert(output_fft_fast == expected)

def tests():
    global DEBUG
    assert(get_pattern(0, 4) == [1,0,-1,0])
    assert(get_pattern(0, 7) == [1,0,-1,0,1,0,-1])
    assert(get_pattern(1, 4) == [0,1,1,0])
    assert(get_pattern(2, 7) == [0,0,1,1,1,0,0])

    test("12345678", 1, "48226158")
    test("12345678", 2, "34040438")
    test("12345678", 3, "03415518")
    test("12345678", 4, "01029498")

    test("80871224585914546619083218645595", 100, "24176176")
    test("19617804207202209144916044189917", 100, "73745418")
    test("69317163492948606335995924319873", 100, "52432133")

    # Part 1
    # DEBUG=True
    if False:
        if DEBUG: print(len(part_one_iput))
        test(part_one_iput, 100, part_one_output[:8])
    else:
        print("Warning: skipping part one - too slow")

    print("All tests passed")

part_one_iput   = "59762574510031092870627555978901048140761858379740610694074091049186715780458779281173757827279664853239780029412670100985236587608814782710381775353184676765362101185238452198186925468994552552398595814359309282056989047272499461615390684945613327635342384979527937787179298170470398889777345335944061895986118963644324482739546009761011573063020753536341827987918039441655270976866933694280743472164322345885084587955296513566305016045735446107160972309130456411097870723829697443958231034895802811058095753929607703384342912790841710546106752652278155618050157828313372657706962936077252259769356590996872429312866133190813912508915591107648889331"
part_one_output = "77038830653233361255314046818347110691571207860972826750703528036072647137275835157934865244753436827100638642075752850257221737315334180111899482275873821050397765752162740703857084466158829110765095716409457347494374275616497668507627323833234935306896546517713172097671580519699518571036198691652639192629112328924296569895346103757993804590618706801045733244530365266348359432626365639551250687317888261896589020351163534902963636024105155028396916635622607564613260090550294620751980641832094142222897182373851955141758381749266214573978629986756691594740935351826234697302504217334139643483903966326398329406895250802553412058415096652193339331"
# answer = fft(part_one_iput, 100)
# print(answer)
# print(answer[:8])

tests()

# import time
# start = time.time()
# out = longer_fft("03036732577212944063491565474664", 100)
# print(out, "(took {:.1f} seconds".format(time.time()-start))

# Want to nick some ideas from real FFT
# Cooley-Turkey FFT algorithm (https://en.wikipedia.org/wiki/Cooley%E2%80%93Tukey_FFT_algorithm)
# sum[0:N-1]{x.n*(wave)} = sum[0:N/2-1]{x.odd*(odd-wave)} + sum[0:N/2-1]{x.even*(even-wave)}
# i.e. divide into 2 halves
# can repeat the divide until the parts are small enough to calculate quickly
#
# strategy...? - requires input to be power-of-two length.

# check adding 0s on the end doesn't affect the answer:
test("8087122458591454661908321864559500000000000000000000", 100, "24176176")
# print("Assumptions ok so far")

def timeit(fun, *args, **kwargs):
    start = time.time()
    ret = fun(*args, **kwargs)
    return (time.time() - start), ret

repeats = 10000

testes = [ ("000000211111111", 2, "67409116"),
           ("03036732577212944063491565474664", repeats, "84462026"),
           ("02935109699940807407585447034323", repeats, "78725270"),
           ("03081770884921959731165446850517", repeats, "53553731")]

for imp_small, reps, expected in testes:
    start_pos = int(imp_small[:7])
    imp_long = imp_small*reps
    # seconds, ans = timeit(longer_fft, imp_small, reps, 100)
    seconds, ans = timeit(fft_fast, imp_long, 100, start_position=start_pos)
    print("{:.0f} seconds for {}*{}".format(seconds, imp_small, reps)); sys.stdout.flush()
    assert(ans == expected)
    print("    -    -    -    -    -")

# seconds, ans = timeit(longer_fft, part_one_iput, repeats, 100)
start_pos = int(part_one_iput[:7])
imp_long = part_one_iput*repeats
seconds, ans = timeit(fft_fast, imp_long, 100, start_position=start_pos)
print("{:.0f} seconds for the main puzzle!".format(seconds))
print("Answer is:", ans)

# 28135104