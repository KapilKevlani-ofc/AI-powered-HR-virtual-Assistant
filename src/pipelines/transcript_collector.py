class TranscriptCollector:
   transcript_parts = []
   @staticmethod
   def reset():
       TranscriptCollector.transcript_parts = []
   @staticmethod
   def add_part(part):
       TranscriptCollector.transcript_parts.append(part)
   @staticmethod
   def get_full_transcript():
       return ' '.join(TranscriptCollector.transcript_parts)