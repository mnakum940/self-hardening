import asyncio
import sys
import os

# Adjust path to find src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from core.system import AegisSystem

async def simulation_loop():
    aegis = AegisSystem()
    
    print("="*60)
    print("      AEGIS V - ACTIVE DEFENSE SIMULATION")
    print("="*60)
    print("Type 'exit' to quit. Type 'reset' to clear session memory.")

    while True:
        try:
            user_input = input("\nUser > ")
            if user_input.lower() == 'exit':
                break
            if user_input.lower() == 'reset':
                aegis.layer2.reset()
                print("[Session Reset]")
                continue
            
            if not user_input.strip():
                continue

            response = await aegis.process_prompt(user_input)
            print(f"Aegis > {response}")
            
            # Allow async tasks (Layer 3) to process
            await asyncio.sleep(0.1)

        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(simulation_loop())
