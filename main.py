from typing import Iterator
import itertools
from pathlib import Path

from workday_job_generator import WDJobGenerator
from workday_job import WDJob

from gpt4all import GPT4All


def find_student_positions() -> Iterator[WDJob]:
    for position in itertools.chain.from_iterable([
        WDJobGenerator(
            base_careers_site_address='https://nvidia.wd5.myworkdayjobs.com',
            careers_page_name='NVIDIAExternalCareerSite',
            wd_company_name='nvidia',
            position_filter={"locationHierarchy1": ["2fcb99c455831013ea52bbe14cf9326c"]}),
        WDJobGenerator(
            base_careers_site_address='https://salesforce.wd12.myworkdayjobs.com',
            careers_page_name='External_Career_Site',
            wd_company_name='salesforce',
            position_filter={"locations": ["26e99ef44f7b1005bacbfb729a5d0000"]})
    ]):
        if any(s.lower() in position.title.lower() for s in ['junior', 'student', 'intern']):
            yield position


def main():
    model_name = 'gpt4all-falcon-newbpe-q4_0.gguf'
    model_directory = Path(__file__).parent / 'models'
    ai_model = GPT4All(model_name=model_name, model_path=model_directory, allow_download=False)

    with ai_model:
        for position in find_student_positions():
            print(position)
            question = f'What are the fields of knowledge I need for the following job position?\n{position.description}'
            print(question)
            print(ai_model.generate(question))


if __name__ == '__main__':
    main()