# Centipede Roguelike

A modern take on the classic Centipede arcade game with roguelike elements including character progression, procedural generation, and strategic upgrades.

## Features

### Classic Centipede Mechanics
- Shoot at descending centipede segments
- Mushroom obstacles that affect centipede movement
- Spider enemies that move unpredictably
- Player movement in the bottom half of the screen

### Roguelike Elements
- **Character Progression**: Gain experience and level up
- **Procedural Generation**: Each wave has randomly placed mushrooms
- **Upgrade System**: Choose from 4 different upgrades when leveling up
- **Shop System**: Spend coins earned from defeating enemies
- **Scaling Difficulty**: Each wave increases enemy count and complexity

### Game Systems
- **Health System**: Take damage from enemies, upgrade max health
- **Experience System**: Gain XP from destroying enemies
- **Currency System**: Earn coins to purchase permanent upgrades
- **Multiple Enemy Types**: Centipede segments, spiders with different behaviors

## Controls

- **Arrow Keys**: Move player
- **Space**: Shoot / Start game
- **1-4**: Select upgrades (during level up)
- **S**: Open shop (from main menu)
- **ESC**: Back to menu (from shop)
- **R**: Restart (after game over)

## Gameplay

### Objective
Survive waves of enemies while growing stronger through experience and upgrades. Each wave features a centipede that moves down the screen, bouncing off mushrooms and walls.

### Progression
- Destroy centipede segments and spiders to gain experience
- Level up to choose from 4 upgrade options:
  1. **Health Boost**: +20 HP and full heal
  2. **Damage Boost**: +10 damage per shot
  3. **Fire Rate**: Shoot faster
  4. **Speed**: Move faster

### Shop
Use coins earned from combat to purchase permanent upgrades:
- Health Boost (10 coins): +25 max HP
- Damage Boost (15 coins): +8 damage
- Fire Rate Boost (12 coins): +3 fire rate

### Strategy Tips
- Centipede segments create mushrooms when destroyed
- Spiders eat mushrooms, changing centipede paths
- Head segments are worth more XP and coins
- Balance offense and defense upgrades
- Use mushrooms as cover and tactical obstacles

## Installation

1. Install Python 3.7+
2. Install pygame:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the game:
   ```bash
   python centipede_roguelike.py
   ```

## Technical Details

- Built with Pygame
- 60 FPS gameplay
- Collision detection system
- State machine for game flow
- Modular enemy and upgrade systems

Enjoy this fusion of classic arcade action with modern roguelike progression!
