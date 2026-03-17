# %%
# import pyperl
# print(dir(pyperl))
# print(pyperl.__version__)

# %%
from pyperl import pyperl

# Initialize
perl = pyperl(verbose='info', installation_dir='c:/temp')
# perl = pyperl(verbose='info')
# perl.clean_installation_dir()

# Get example audio file
audio_file = perl.import_example()

# Run perl script for audio conversion using ffmpeg
out = perl.run(audio_file, "c:/temp/output.mp3")


# %%
from pyperl import pyperl

# Initialize
perl = pyperl(verbose='info', force_install=False)

# Perl script is located here
perl.script

# Perl path location is here
perl.perl_path


