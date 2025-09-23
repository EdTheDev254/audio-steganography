import wave

def analyze_wav_capacity(wav_file_path):
    """
    Analyzes a WAV file to show its properties and calculates the maximum
    data that can be hidden within it.
    """
    try:
        with wave.open(wav_file_path, 'rb') as song:
            n_channels = song.getnchannels()
            samp_width = song.getsampwidth()
            frame_rate = song.getframerate()
            n_frames = song.getnframes()
            
            duration_in_seconds = n_frames / float(frame_rate)
            bit_depth = samp_width * 8
            channel_str = "Stereo" if n_channels == 2 else "Mono"
            
            total_audio_bytes = n_frames * n_channels * samp_width
            
            header_size = 32
            available_bits_for_message = total_audio_bytes - header_size
            max_bytes = available_bits_for_message // 8

            if max_bytes <= 0:
                print("Error: File is too short to hide any data.")
                return 0

            if max_bytes > 1024 * 1024:
                readable_size = f"{max_bytes / (1024*1024):.2f} MB"
            elif max_bytes > 1024:
                readable_size = f"{max_bytes / 1024:.2f} KB"
            else:
                readable_size = f"{max_bytes} bytes"

            print("-" * 40)
            print(f"Analysis Report for: '{wav_file_path}'")
            print(f"  - Channels: {n_channels} ({channel_str})")
            print(f"  - Sample Rate: {frame_rate:,} Hz")
            print(f"  - Bit Depth: {bit_depth}-bit")
            print(f"  - Duration: {duration_in_seconds:.2f} seconds")
            print(f"  - Raw Audio Size: {total_audio_bytes:,} bytes")
            print("-" * 40)
            print(f"Maximum Storage Capacity: {max_bytes:,} bytes ({readable_size})")
            print("-" * 40)
            return max_bytes
            
    except FileNotFoundError:
        print(f"Error: The file '{wav_file_path}' was not found.")
        return None
    except wave.Error as e:
        print(f"Error: Not a valid WAV file or file is corrupted. Details: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def hide_data_in_wav(input_wav_path, output_wav_path, secret_message):
    """
    Hides a secret message in a WAV file using the interleaved LSB method.
    """
    print("Hiding message...")
    try:
        with wave.open(input_wav_path, mode='rb') as song:
            frames = bytearray(song.readframes(song.getnframes()))
            params = song.getparams()
            
        message_bytes = secret_message.encode('utf-8')
        binary_message = ''.join(f'{byte:08b}' for byte in message_bytes)
        message_length_bits = len(binary_message)
        length_header = f'{message_length_bits:032b}'
        
        total_frames_bytes = len(frames)
        header_size = 32
        
        if (header_size + message_length_bits) > total_frames_bytes:
            raise ValueError("Error: The message is too long for this audio file.")

        # Embed the header
        for i in range(header_size):
            if length_header[i] == '1':
                frames[i] |= 1
            else:
                frames[i] &= 254
        
        # Embed the message body (interleaved)
        frames_for_body = total_frames_bytes - header_size
        step = frames_for_body // message_length_bits
        
        print(f"Using a step rate of {step} to interleave data.")
        frame_index = header_size
        for bit in binary_message:
            if bit == '1':
                frames[frame_index] |= 1
            else:
                frames[frame_index] &= 254
            frame_index += step

        with wave.open(output_wav_path, 'wb') as fd:
            fd.setparams(params)
            fd.writeframes(frames)
            
        print(f"Message hidden successfully in '{output_wav_path}'")

    except FileNotFoundError:
        print(f"Error: The file '{input_wav_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def extract_data_from_wav(input_wav_path):
    """
    Extracts a message from a WAV file hidden with the interleaved method.
    """
    print("Extracting message...")
    try:
        with wave.open(input_wav_path, mode='rb') as song:
            frames = song.readframes(song.getnframes())
            
            header_size = 32
            if len(frames) < header_size:
                return "Error: File is too short to contain a valid header."

            length_bits = "".join(str(byte & 1) for byte in frames[:header_size])
            message_length_bits = int(length_bits, 2)

            frames_for_body = len(frames) - header_size
            if message_length_bits == 0:
                return "Message length is zero, nothing to extract."
            if message_length_bits > frames_for_body:
                return "Error: Message length in header is larger than the file size."
            
            step = frames_for_body // message_length_bits

            extracted_bits = []
            frame_index = header_size
            for _ in range(message_length_bits):
                extracted_bits.append(str(frames[frame_index] & 1))
                frame_index += step
            
            binary_message = "".join(extracted_bits)
            message_bytes = bytearray(int(binary_message[i:i+8], 2) for i in range(0, len(binary_message), 8))
            message = message_bytes.decode('utf-8', errors='ignore')
            
            return message

    except FileNotFoundError:
        return f"Error: The file '{input_wav_path}' was not found."
    except Exception as e:
        return f"An error occurred: {e}"

# --- Main Program ---
if __name__ == '__main__':
    while True:
        choice = input("Do you want to (e)ncode or (d)ecode a message? (e/d): ").lower()
        if choice in ['e', 'd']:
            break
        print("Invalid choice. Please enter 'e' or 'd'.")

    if choice == 'e':
        carrier_file = input("Enter the path to the carrier WAV file (e.g., carrier.wav): ")
        
        max_bytes = analyze_wav_capacity(carrier_file)
        if max_bytes is not None and max_bytes > 0:
            output_file = input("Enter the path for the output WAV file (e.g., output.wav): ")
            
            secret_message = """In the heart of Elizabethan England, a man of humble beginnings would emerge to become the most celebrated writer in the English language, a playwright whose genius would transcend time and resonate through the centuries. This is the story of William Shakespeare, a name synonymous with literary greatness.
Born in the bustling market town of Stratford-upon-Avon in April 1564, William was the son of John Shakespeare, a glove-maker and prominent town official, and Mary Arden, the daughter of a prosperous farmer.[1] His father's civic standing likely afforded William a place at the local King Edward VI Grammar School, where he would have received a rigorous education in Latin and classical literature, laying the foundation for his future literary endeavors.[2]
In 1582, at the age of 18, Shakespeare married Anne Hathaway, a woman eight years his senior.[1] Their union was hastened by Anne's pregnancy, and they would go on to have three children: Susanna, and twins Hamnet and Judith.[1] Tragedy would strike the family in 1596 with the death of their only son, Hamnet, at the age of 11, a loss that undoubtedly cast a long shadow over Shakespeare's life and is believed to have influenced some of his later, more somber plays.[1]
Following the birth of his twins, a period of roughly seven years, from 1585 to 1592, remains largely undocumented, a time scholars refer to as the "lost years."[2] Speculation abounds as to what Shakespeare was doing during this time, with theories ranging from him working as a schoolmaster to him fleeing Stratford after a deer-poaching incident. Whatever the truth, by 1592, he had emerged in the vibrant and competitive theatrical world of London.
His arrival in the capital was not without its challenges. A bitter rival, Robert Greene, famously derided him as an "upstart Crow, beautified with our feathers." This jealous jab, however, was a clear indication that Shakespeare was already making a name for himself as both an actor and a playwright. His early plays, believed to have been written around this time, included historical dramas like the Henry VI trilogy and Richard III, comedies such as The Taming of the Shrew and The Comedy of Errors, and the bloody tragedy of Titus Andronicus.[3]
The 1590s proved to be a pivotal decade for Shakespeare. He became a founding member and the principal playwright of the Lord Chamberlain's Men, an acting company that would become the most successful of its time.[4] This troupe, which included the celebrated actor Richard Burbage, performed at various theaters before eventually building their own iconic playhouse, the Globe Theatre, in 1599.[5] The Globe, an open-air amphitheater on the south bank of the River Thames, became the stage for many of Shakespeare's most famous works.[5]
During this period, Shakespeare's writing flourished, and he produced a remarkable string of beloved comedies and histories. Plays like A Midsummer Night's Dream, The Merchant of Venice, Much Ado About Nothing, and As You Like It captivated audiences with their witty wordplay, intricate plots, and memorable characters.[6] He also penned poignant historical dramas such as Richard II, Henry IV, Parts 1 and 2, and Henry V, which explored the complexities of power and politics.[6]
The turn of the century marked a shift in Shakespeare's writing, as he delved into the depths of human suffering and despair with a series of profound tragedies that are considered the pinnacle of his art. Hamlet, Othello, King Lear, and Macbeth, all written in the early 1600s, are timeless explorations of themes like revenge, jealousy, madness, and ambition.[3] These plays are characterized by their psychological depth, poetic language, and unforgettable tragic heroes.
In 1603, following the death of Queen Elizabeth I and the ascension of King James I, the Lord Chamberlain's Men were granted a royal patent and became known as the King's Men, solidifying their status as the preeminent acting company in England.[1] Shakespeare continued to write for the company, and his work from this Jacobean period saw him experiment with genre, producing what are now known as the "romances" or tragicomedies. Plays like The Winter's Tale and The Tempest blend elements of comedy and tragedy, often culminating in themes of forgiveness and reconciliation.[7]
Beyond his dramatic works, Shakespeare was also a masterful poet. In 1609, a collection of his 154 sonnets was published, though many were likely written in the 1590s.[6][8] These intricate and emotionally charged poems explore themes of love, beauty, time, and mortality.[8] The sonnets are largely divided into two sequences: the first addressed to a "Fair Youth," urging him to marry and have children to preserve his beauty, and the second to a "Dark Lady," a mysterious and often tormenting lover.[9] The Shakespearean sonnet, a form consisting of three quatrains and a final couplet in iambic pentameter, became a standard in English poetry, a testament to his influence.[8][10]
Shakespeare's success in the London theater made him a wealthy man. He was a shrewd businessman, investing in property in both London and his hometown of Stratford. In 1597, he purchased New Place, one of the largest houses in Stratford-upon-Avon, a clear symbol of his elevated social standing.[11] Though his professional life was centered in London, he maintained strong ties to his family and community in Stratford, where he would eventually retire.
Sometime around 1611, Shakespeare appears to have largely withdrawn from the London stage and returned to Stratford to live the life of a country gentleman.[11] He continued to have business dealings and collaborate with other playwrights, such as John Fletcher, on his final plays, including Henry VIII and The Two Noble Kinsmen.[7]
William Shakespeare died on April 23, 1616, at the age of 52.[11] The cause of his death is unknown, though a diary entry from a contemporary suggests it may have been the result of a fever contracted after a night of drinking with fellow playwrights Ben Jonson and Michael Drayton.[12] He was buried in the chancel of the Holy Trinity Church in Stratford-upon-Avon.[11] In his will, he famously left his wife his "second-best bed," a bequest that has been the subject of much speculation but was not necessarily the slight it might seem today.[1]
Seven years after his death, two of his fellow actors, John Heminges and Henry Condell, compiled and published a collection of his plays known as the First Folio.[7] This volume, which included 36 plays, was instrumental in preserving Shakespeare's work for future generations."""

            message_byte_count = len(secret_message.encode('utf-8'))
            print(f"\nMessage to encode contains {len(secret_message):,} characters (UTF-8 size: {message_byte_count:,} bytes).")

            if message_byte_count > max_bytes:
                print(f"Warning: Your message is {message_byte_count} bytes long, but only {max_bytes} can be hidden.")
            else:
                hide_data_in_wav(carrier_file, output_file, secret_message)
                
    elif choice == 'd':
        stego_file = input("Enter the path to the WAV file with the hidden message (e.g., output.wav): ")
        hidden_message = extract_data_from_wav(stego_file)
        print(f"\nSecret message found:\n---")
        print(hidden_message)
        print("---")