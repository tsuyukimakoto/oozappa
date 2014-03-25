from oozappa.fabrictools import upload_template

def _deploy_template_sample_a(context):
    upload_template('sample_a.txt', '/home/makoto/sample_a.conf', context=context)
