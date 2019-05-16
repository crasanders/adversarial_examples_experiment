from psychopy import core, visual, event
import numpy as np
from os.path import join
import pandas as pd

imsize = 299
mask_size = 256
units = 'pix'
nmasks = 10
frame_rate = 1 / 60
keys = ['f', 'j']
nstim = 3
nprac = 3
stimuli_dir = 'stimuli'
data_dir = 'data'
cats_dir = join(stimuli_dir, 'cat')
dogs_dir = join(stimuli_dir, 'dog')
false_dir = join(stimuli_dir, 'false')
ttype_labels = {'adv': 'Adversarial Trial', 'flp': 'Flip Trial', 'img': 'Image Trial', 'prac': 'Practice Trial'}
false_labels = {'cat': 'flt', 'dog': 'fls', 'neither': 'img'}

fixation_min_time = .500
fixation_max_time = 1.000
stim_presentation_time = .063
mask_presentation_time = .020
trial_time = 2.200

fixation_min_frames = round(fixation_min_time / frame_rate)
fixation_max_frames = round(fixation_max_time / frame_rate)
stim_presentation_frames = round(stim_presentation_time / frame_rate)
mask_presentation_frames = round(mask_presentation_time / frame_rate)
trial_frames = round(trial_time / frame_rate)

subject_id = core.getAbsTime()
key_assignment = np.random.randint(0, 2)
response_keys = {'Cat': keys[key_assignment], 'Dog': keys[not key_assignment]}

screen_width = 800
screen_height = 800

instruction_text = \
"On each trial of this experiment, you will see a + in the center of the screen. Stare at the +. After a moment, an \
image will briefly appear and disappear, followed by irrelevant scrambled images. Your job is to identify the image. \
You should try to make as few mistakes as possible, but you should also always try to respond as fast as you can. You \
will first do some practice trials. \n \
\n \
Press any key to continue."

practice_text = \
"If the image is a {} press the F key. If the image is a {} press the J key. Sometimes it may be hard to tell if the \
image is a cat or dog, but you should go with your first impression. \n \
Press any key to continue.".format(['Cat', 'Dog'][key_assignment], ['Cat', 'Dog'][not key_assignment])

f_key_text = 'Press the F key'
j_key_text = 'Press the J key'

prac_over_text = "The practice is now over. Remember, if the image is a {} press the F key. If the image is a {} press \
the J key. You should try to make as few mistakes as possible, but you should also always try to respond as fast as \
you can.  Sometimes it may be hard to tell if the image is a cat or dog, but you should go with your first impression. \
\n \n Press any key to start the experiment.".format(['Cat', 'Dog'][key_assignment], ['Cat', 'Dog'][not key_assignment])

practice_stimuli = []
for s in range(nprac):
    sid = str(s).zfill(5)

    r = 'prac'

    image = join(cats_dir, r, '{}{}.png'.format(r, sid))
    ttype = ttype_labels[r]
    practice_stimuli.append({'Image': image, 'Category': 'Cat', 'Trial_Type': ttype,
                             'Stimulus_ID': 'Cat' + sid})

    image = join(dogs_dir, r, '{}{}.png'.format(r, sid))
    ttype = ttype_labels[r]
    practice_stimuli.append({'Image': image, 'Category': 'Dog', 'Trial_Type': ttype,
                             'Stimulus_ID': 'Dog' + sid})

np.random.shuffle(practice_stimuli)
for t, stim in enumerate(practice_stimuli):
    stim['Trial'] = t - nprac * 2 + 1

trial_stimuli = []
for s in range(nstim):
    sid = str(s).zfill(5)

    r = np.random.choice(['adv', 'flp', 'img'])
    image = join(cats_dir, r, '{}{}.png'.format(r, sid))
    ttype = ttype_labels[r]
    trial_stimuli.append({'Image': image, 'Category': 'Cat', 'Trial_Type': ttype,
                          'Stimulus_ID': 'Cat' + sid})

    r = np.random.choice(['adv', 'flp', 'img'])
    image = join(dogs_dir, r, '{}{}.png'.format(r, sid))
    ttype = ttype_labels[r]
    trial_stimuli.append({'Image': image, 'Category': 'Dog', 'Trial_Type': ttype,
                          'Stimulus_ID': 'Dog' + sid})

    r = np.random.choice(['cat', 'dog', 'neither'])
    label = false_labels[r]
    image = join(false_dir, r, '{}{}.png'.format(label, sid))
    trial_stimuli.append({'Image': image, 'Category': r.title(), 'Trial_Type': 'False Trial',
                          'Stimulus_ID': 'False' + sid})

np.random.shuffle(trial_stimuli)
for t, stim in enumerate(trial_stimuli):
    stim['Trial'] = t+1


def trial(stimulus):
    stim = visual.ImageStim(win, image=stimulus['Image'], size=(imsize, imsize), units=units)

    fixation = visual.TextStim(win, text='+', units='norm', height=.2, color=[-1, -1, -1])
    fixation_frames = np.random.randint(fixation_min_frames, fixation_max_frames+1)
    for frame in range(fixation_frames):
        fixation.draw()
        win.flip()

    rt_clock = core.Clock()
    for frame in range(stim_presentation_frames):
        stim.draw()
        win.flip()

    win.flip()
    event.clearEvents()

    mask = visual.GratingStim(win, size=(imsize, imsize), units=units)
    for m in range(nmasks):
        rand = np.sign(np.random.rand(mask_size, mask_size) * 2 - 1)
        mask.tex = rand
        for frame in range(mask_presentation_frames):
            mask.draw()
            win.flip()
    for frame in range(trial_frames):
        win.flip()
    keys_pressed = event.getKeys(keyList=keys, timeStamped=rt_clock)

    if not keys_pressed:
        faster_prompt = visual.TextStim(win, text='Please respond more quickly.', units='norm', height=.05,
                                        color=[-1, -1, -1])
        faster_prompt.draw()
        win.flip()
        core.wait(2)
        key_press = (np.nan, np.nan)
    else:
        key_press = keys_pressed[0]

    stimulus['Subject_ID'] = subject_id
    stimulus['Response'] = key_press[0]
    if not np.isnan(key_press[1]):
        stimulus['RT'] = int(key_press[1] * 1000)
    else:
        stimulus['RT'] = np.nan

    return stimulus


win = visual.Window((screen_width, screen_height), monitor='testMonitor', allowGUI=False, color='white')

instructions = visual.TextStim(win, text=instruction_text, height=.05, color=[-1, -1, -1])
instructions.draw()
win.flip()
event.waitKeys()

practice = visual.TextStim(win, text=practice_text, color=[-1, -1, -1], pos=(0, 180), units=units)

if key_assignment == 0:
    cat_pic = visual.ImageStim(win, image='stimuli/example_cat.jpg', size=(imsize, imsize), units=units, pos=(-150, 0))
    dog_pic = visual.ImageStim(win, image='stimuli/example_dog.jpg', size=(imsize, imsize), units=units, pos=(150, 0))

else:
    cat_pic = visual.ImageStim(win, image='stimuli/example_cat.jpg', size=(imsize, imsize), units=units, pos=(150, 0))
    dog_pic = visual.ImageStim(win, image='stimuli/example_dog.jpg', size=(imsize, imsize), units=units, pos=(-150, 0))

f_key = visual.TextStim(win, text=f_key_text, color=[-1, -1, -1], pos=(-150, -160), units=units)
j_key = visual.TextStim(win, text=j_key_text, color=[-1, -1, -1], pos=(150, -160), units=units)

practice.draw()
cat_pic.draw()
dog_pic.draw()
f_key.draw()
j_key.draw()

win.flip()
event.waitKeys()

trial_data = []
for practice_stimulus in practice_stimuli:
    start_next_trial = visual.TextStim(win, text='Press any key to start the next trial.', units='norm', height=.05,
                                       color=[-1, -1, -1])
    start_next_trial.draw()
    win.flip()
    event.waitKeys()
    trial_data.append(trial(practice_stimulus))

instructions = visual.TextStim(win, text=prac_over_text, height=.05, color=[-1, -1, -1])
instructions.draw()
win.flip()
event.waitKeys()

for trial_stimulus in trial_stimuli:
    start_next_trial = visual.TextStim(win, text='Press any key to start the next trial.', units='norm', height=.05,
                                       color=[-1, -1, -1])
    start_next_trial.draw()
    win.flip()
    event.waitKeys()
    trial_data.append(trial(trial_stimulus))

pd.DataFrame(trial_data).to_csv(join(data_dir, "adv_ex_{}.csv".format(subject_id)), index=False)
win.close()
