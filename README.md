# Self.Py Progress Migration (SPPM)

## Intro
The [self.py course](https://campus.gov.il/course/course-v1-cs-gov_cs_selfpy101/), 
a beginners Python <abbr title="Massive Open Online Course">MOOC</abbr> at 
[Campus IL](https://campus.gov.i), has a half-year cycle (summer/winter). At the
end of a cycle, the old course is archived (viewable, but no longer active) and 
a new course is opened.

Participants of the old cycle may continue on new cycle, but they need to 
manually re-answer, or copy, all their submitted exercises from old cycle 
to the new one (29 exercise pages).

I do recommend re-answering as a way of strengthening the knowledge learned so 
far. Yet, if one is going to just manually copy his old answers, it might be a 
boring and time-consuming chore.

## What this script do?
Using selenium (with Chrome driver) it automatically migrates self.py course's
progress from old cycle to the new one. Using participants account, it goes 
over each closed-exercise, copy the old answers, insert and submit them at new 
cycle course pages. 

## Usage
### Pre-requests:
 1. Python version 3.8+
 2. Install selenium package. Can be done with this command:
    `pip install -U selenium`
 3. Install **WebDriver for Chrome** (from: 
https://sites.google.com/chromium.org/driver/downloads) and add its location to 
system's path ([read more about it here](https://www.selenium.dev/documentation/en/webdriver/driver_requirements/)).
 4. Make sure you have _**conf.ini**_ (or _**conf.ini.sample**_) file in same 
directory as `sppm.py` file.

### Running script 
From your command prompt (cmd) use this command:
`python sppm.py`

You will be prompted for your Campus IL login's email/password (unless already 
set in conf.ini file).

After a few seconds you should see a new window of Google Chrome browser opens. 
Don't touch it and let the automation run. Expected automation run-time is 5-10 minutes.

### Customisation
#### Limit exercises to migrate
If not all 29 are done in old cycle, a shorter run-time can be done by adding the last exercise to migrate in configuration file. If, for example, the last exercise done is: 7.1.3, update _**conf.ini**_ like this:
```buildoutcfg
[EXERCISES]
LAST=7.1.3
```

#### Update different course cycles
This script was written for migration between the 1st and the 2nd cycles of 2021. If you need to migrate between different cycles, edit configuration file [CYCLES] section.

Identify cycle's sub-string in curse address - it is usually the year and the cycle number (1 or 2) connected by an underscore - see bold text in address below:

> courses.campus.gov.il/courses/course-v1:CS+GOV_CS_selfpy101+**2020_2**/info
 
Update it in the section below (at _**conf.ini**_):

```buildoutcfg
[CYCLES]
COURSE=course-v1:CS+GOV_CS_selfpy101
OLD=1_2021
NEW=2021_2
```

## Disclaimer
This content is not affiliated with, endorsed, sponsored, or specifically approved by Campus-IL, National Cyber Directorate or anyone else related to self.py course, and they are not responsible for it.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
