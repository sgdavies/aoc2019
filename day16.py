DEBUG=False

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

def longer_fft(input_signal, phases):
    output_position = int(input_signal[:8])
    print("Will look for output at position:", output_position)
    input_signal = input_signal*1000

    output_signal = fft(input_signal, phases)
    return output_signal[output_position:output_position+1]

def test(input_signal, phases, expected):
    output = fft(input_signal, phases, length=len(expected))
    if DEBUG: print(output, '\n', expected)
    assert(output == expected)

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
print("Assumptions ok so far")