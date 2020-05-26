VALID_AUDIO='valid_audio'
INVALID_AUDIO='invalid_audio'

DEFAULT_ENCODING='utf-8'

FEATURE_PORT=5560
VALIDATE_PORT=5555
PREDICT_PORT=5565

MFCC = 'mfcc'
C_CENS = 'c_cens'
MEL = 'mel'
C_CQT = 'c_cqt'
C_STFT = 'c_stft'

feature_model_dirs = {
    MFCC: 'mfcc',
    C_CENS: 'chroma_cens',
    MEL: 'melspectrogram',
    C_CQT: 'chroma_cqt',
    C_STFT: 'chroma_stft'
}
