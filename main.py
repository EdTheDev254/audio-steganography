import wave
# --- The Key Change: Import the message from the separate file ---
from message_container import secret_message

# This constant is based on the discovery that a step rate of 100 or more
# makes the hidden data imperceptible by spreading the bits far apart.
STEALTH_STEP_RATE_THRESHOLD = 180

def analyze_wav_capacity(wav_file_path):
    """
    Analyzes a WAV file to show its properties and calculates both the absolute
    maximum and the recommended "stealthy" storage capacity.
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
            available_bytes = total_audio_bytes - header_size

            abs_max_bytes = available_bytes // 8
            stealth_max_bytes = available_bytes // (8 * STEALTH_STEP_RATE_THRESHOLD)

            if abs_max_bytes <= 0:
                print("Error: File is too short to hide any data.")
                return None, None

            def format_size(byte_count):
                if byte_count > 1024 * 1024:
                    return f"{byte_count / (1024*1024):.2f} MB"
                elif byte_count > 1024:
                    return f"{byte_count / 1024:.2f} KB"
                else:
                    return f"{byte_count} bytes"

            print("-" * 40)
            print(f"Analysis Report for: '{wav_file_path}'")
            print(f"  - Channels: {n_channels} ({channel_str})")
            print(f"  - Sample Rate: {frame_rate:,} Hz")
            print(f"  - Bit Depth: {bit_depth}-bit")
            print(f"  - Duration: {duration_in_seconds:.2f} seconds")
            print(f"  - Raw Audio Size: {total_audio_bytes:,} bytes")
            print("-" * 40)
            print("CAPACITY REPORT:")
            print(f"  - Absolute Maximum:  {abs_max_bytes:,} bytes ({format_size(abs_max_bytes)})")
            print(f"  - Stealth Capacity (No Hiss): {stealth_max_bytes:,} bytes ({format_size(stealth_max_bytes)})")
            print("-" * 40)
            
            return abs_max_bytes, stealth_max_bytes
            
    except FileNotFoundError:
        print(f"Error: The file '{wav_file_path}' was not found.")
        return None, None
    except Exception as e:
        print(f"An unexpected error occurred during analysis: {e}")
        return None, None


def hide_data_in_wav(input_wav_path, output_wav_path, message_to_hide):
    """
    Hides a secret message in a WAV file using the interleaved LSB method.
    """
    print("Hiding message...")
    try:
        with wave.open(input_wav_path, mode='rb') as song:
            frames = bytearray(song.readframes(song.getnframes()))
            params = song.getparams()

        message_bytes = message_to_hide.encode('utf-8')
        binary_message = ''.join(f'{byte:08b}' for byte in message_bytes)
        message_length_bits = len(binary_message)
        length_header = f'{message_length_bits:032b}'
        
        total_frames_bytes = len(frames)
        header_size = 32
        
        if (header_size + message_length_bits) > total_frames_bytes:
            raise ValueError("Message too long for this file.")

        for i in range(header_size):
            if length_header[i] == '1': frames[i] |= 1
            else: frames[i] &= 254
        
        frames_for_body = total_frames_bytes - header_size
        step = frames_for_body // message_length_bits
        
        print(f"Using a step rate of {step} to interleave data.")
        frame_index = header_size
        for bit in binary_message:
            if bit == '1': frames[frame_index] |= 1
            else: frames[frame_index] &= 254
            frame_index += step

        with wave.open(output_wav_path, 'wb') as fd:
            fd.setparams(params)
            fd.writeframes(frames)
        print(f"Message hidden successfully in '{output_wav_path}'")

    except Exception as e:
        print(f"An error occurred during encoding: {e}")


def extract_data_from_wav(input_wav_path):
    """
    Extracts a message from a WAV file hidden with the interleaved method.
    """
    print("Extracting message...")
    try:
        with wave.open(input_wav_path, mode='rb') as song:
            frames = song.readframes(song.getnframes())
            
            header_size = 32
            if len(frames) < header_size: return "Error: File is too short."

            length_bits = "".join(str(byte & 1) for byte in frames[:header_size])
            message_length_bits = int(length_bits, 2)

            frames_for_body = len(frames) - header_size
            if message_length_bits == 0: return "No message found."
            if message_length_bits > frames_for_body: return "Error: Corrupted file."
            
            step = frames_for_body // message_length_bits
            if step == 0: return "Error: Invalid step rate, cannot extract."

            extracted_bits = []
            frame_index = header_size
            for _ in range(message_length_bits):
                extracted_bits.append(str(frames[frame_index] & 1))
                frame_index += step
            
            binary_message = "".join(extracted_bits)
            message_bytes = bytearray(int(binary_message[i:i+8], 2) for i in range(0, len(binary_message), 8))
            return message_bytes.decode('utf-8', errors='ignore')

    except FileNotFoundError:
        return f"Error: The file '{input_wav_path}' was not found."
    except Exception as e:
        return f"An error occurred during extraction: {e}"


# --- Main Program ---
if __name__ == '__main__':
    while True:
        choice = input("Do you want to (e)ncode or (d)ecode a message? (e/d): ").lower()
        if choice in ['e', 'd']: break
        print("Invalid choice. Please enter 'e' or 'd'.")

    if choice == 'e':
        carrier_file = input("Enter the path to the carrier WAV file (e.g., carrier.wav): ")
        
        abs_max_bytes, stealth_max_bytes = analyze_wav_capacity(carrier_file)
        
        if abs_max_bytes is not None and abs_max_bytes > 0:
            output_file = input("Enter the path for the output WAV file (e.g., output.wav): ")
            
            # The script now automatically uses the message from message_container.py
            print(f"\nUsing secret message from 'message_container.py'.")
            
            message_byte_count = len(secret_message.encode('utf-8'))
            print(f"Message to encode contains {len(secret_message):,} characters ({message_byte_count:,} bytes).")

            if message_byte_count > abs_max_bytes:
                print("\nERROR: Message is too large for this file's absolute capacity.")
            elif message_byte_count > stealth_max_bytes:
                print("\nWARNING: Message exceeds the recommended stealth capacity.")
                print("The resulting step rate will be less than 100, which may produce audible noise.")
                proceed = input("Do you want to continue anyway? (y/n): ").lower()
                if proceed == 'y':
                    hide_data_in_wav(carrier_file, output_file, secret_message)
            else:
                print("\nMessage is within stealth capacity. Proceeding with encoding.")
                hide_data_in_wav(carrier_file, output_file, secret_message)
                
    elif choice == 'd':
        stego_file = input("Enter the path to the WAV file with the hidden message (e.g., output.wav): ")
        hidden_message = extract_data_from_wav(stego_file)
        print(f"\nSecret message found:\n---")
        print(hidden_message)
        print("---")