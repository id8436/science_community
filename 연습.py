from googletrans import Translator as googleTrans

googletranslator = googleTrans()
print(googletranslator.detect('이 언어는 한국어입니다.'))
print(googletranslator.detect('veritas lux mea'))
detection = googletranslator.detect('こんにちは')
print(detection.lang)