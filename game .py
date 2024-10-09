import pygame
import os
import random
from itertools import groupby

class Card():
    loaded_images = {}  # 类变量，用于存储加载的图像

    def __init__(self):
        self.color = None
        self.value = None
        self.points = 0
        self.colorDict = {1: "1", 2: "2", 3: "3", 4: "4", 5: "5"}
        self.valueDict = {10: "0a", 11: "0b", 12: "0c", 13: "0d", 14: '0e', 15: '0f'}
        self.x = 0
        self.y = 0

    @staticmethod
    def load_images(card_display_width, card_display_height):
        for color in range(1, 6):
            for value in range(1, 16):
                card = Card()
                card.createSpecificCard(color, value)
                image = pygame.image.load(card.filename())
                scaled_image = pygame.transform.scale(image, (card_display_width, card_display_height))
                Card.loaded_images[card.filename()] = scaled_image

        # 加载鬼牌的图像
        for joker_color in ['black', 'red']:
            joker_image = pygame.image.load(f'pics/{joker_color}.png')
            scaled_joker_image = pygame.transform.scale(joker_image, (card_display_width, card_display_height))
            Card.loaded_images[f'pics/{joker_color}.png'] = scaled_joker_image

        # 加载牌背的图像
        back_image = pygame.image.load('pics/tileBack.png')
        Card.loaded_images['back'] = pygame.transform.scale(back_image, (card_display_width, card_display_height))

    def create_deck(self):
        deck = []
        for color in range(1, 6):  # 5种颜色的牌
            for value in range(1, 16):  # 每种颜色15张牌
                card = Card()
                card.createSpecificCard(color, value)
                deck.append(card)

        # 添加两张鬼牌
        black_joker = Card()
        black_joker.create_joker('black')
        deck.append(black_joker)

        red_joker = Card()
        red_joker.create_joker('red')
        deck.append(red_joker)

        random.shuffle(deck)
        return deck

    def createSpecificCard(self, s, v):
        self.color = s
        self.value = v
        self.calculate_points()

    def create_joker(self, color):
        self.color = color
        self.value = 0
        self.points = 0


    def calculate_points(self):
        if 1 <= self.value <= 9:
            self.points = self.value
        else:   
            self.points = 10

    def filename(self):
        # 首先检查是否为鬼牌
        if self.color in ['black', 'red']:
            return f'pics/{self.color}.png'

        fn = "pics/"
        fn += self.colorDict[self.color] + "-"
        if 1 <= self.value <= 9:
            fn += str(self.value).zfill(2)
        else:
            fn += self.valueDict[self.value]
        fn += ".png"
        return fn

    def setPosition(self, x, y):
        self.x = x
        self.y = y

    def get_scaled_image(self, target_width, target_height):
        image = Card.loaded_images[self.filename()]
        scaled_rect = image.get_rect().move(self.x, self.y)
        return image, scaled_rect
    def get_scaled_rect(self, target_width, target_height):
        _, scaled_rect = self.get_scaled_image(target_width, target_height)
        return scaled_rect

class RummikubGame():
    def __init__(self):
        self.players = []
        self.current_player = 0
        self.round = 1
        self.break_ice = False
        self.public_pouch = []
        self.card_display_width = 70
        self.card_display_height = 90
        self.deck = Card().create_deck()  # 创建一个新的牌堆

    def start_game(self):
        for _ in range(4):  # 假设有四个玩家
            player_hand = self.deck[:10]  # 为每个玩家分配前十张牌
            self.deck = self.deck[10:]  # 从牌堆中移除已分配的牌
            self.players.append(player_hand)

        # 初始化公共牌堆
        self.public_pouch = self.deck  # 公共牌堆为剩余的牌
        random.shuffle(self.public_pouch)

    def is_valid_combination(self, cards):
        # 确保卡片列表非空且至少有三张卡片
        if not cards or len(cards) < 3:
            return False

        # 检查是否所有卡片都是同一颜色
        if all(card.color == cards[0].color for card in cards):
            sorted_cards = sorted(cards, key=lambda x: x.value)
            if all(card.value % 2 == sorted_cards[0].value % 2 for card in sorted_cards):
                if all(sorted_cards[i].value == sorted_cards[i-1].value + 2 for i in range(1, len(sorted_cards))):
                    return True

        # 检查是否所有卡片数字相同但颜色不同
        if all(card.value == cards[0].value for card in cards):
            unique_colors = set(card.color for card in cards)
            if len(unique_colors) == len(cards):
                return True

        return False

    def display_player_hand(self, screen, player_hand, hand_area_slots):
        for i, card in enumerate(player_hand):
            # 确定卡片位置
            card.setPosition(hand_area_slots[i].x, hand_area_slots[i].y)
            # 显示卡片
            card_image, card_rect = card.get_scaled_image(self.card_display_width, self.card_display_height)
            screen.blit(card_image, card_rect)


    def add_to_game_area(self, current_player_hand, cardList):
        if self.is_valid_combination(cardList):
            current_player_hand.clear()
            return True
        return False

    def play_turn(self, screen, cardList):
        current_player_hand = self.players[self.current_player]
        if not self.break_ice:
            total_points = sum(card.points for card in current_player_hand)
            if total_points >= 30:
                self.break_ice = True
            else:
                print("You need to show at least 30 points in the first round.")
                pygame.quit()
        else:
            added_to_game = self.add_to_game_area(current_player_hand, cardList)
            if not added_to_game:
                build_successful = self.build_on_existing_sets(current_player_hand, cardList)
                if not build_successful:
                    drawn_tile_1 = self.draw_tile_from_pool()
                    drawn_tile_2 = self.draw_tile_from_pool()
                    chosen_tile = self.choose_tile_to_add(drawn_tile_1, drawn_tile_2)
                    current_player_hand.append(chosen_tile)
        screen.fill(pygame.Color('aquamarine4'))
        for card in cardList:
            card_image, card_rect = card.get_scaled_image(self.card_display_width, self.card_display_height)
            screen.blit(card_image, card_rect)
        pygame.display.update()

    def draw_two_tiles(self):
        if len(self.public_pouch) >= 2:
            tile1 = self.public_pouch.pop()
            tile2 = self.public_pouch.pop()
            tile1.setPosition(300, 200)  # 第一张牌的位置
            tile2.setPosition(400, 200)  # 第二张牌的位置
            return [tile1, tile2]
        elif len(self.public_pouch) == 1:
            tile = self.public_pouch.pop()
            tile.setPosition(300, 200)  # 如果只剩一张牌，显示在这个位置
            return [tile, None]
        return [None, None]

    def choose_tile_to_add(self, tile1, tile2):
        return tile1

    def build_on_existing_sets(self, current_player_hand, cardList):
        if cardList:
            cardList.extend(current_player_hand)
            current_player_hand.clear()
            return True
        return False
    def robot_turn(self, player_index):
        
        # 此处可根据游戏规则添加更复杂的策略
        player_hand = self.players[player_index]
        # 检查手牌中是否有有效的组合
        for i in range(len(player_hand)):
            for j in range(i + 1, len(player_hand)):
                if self.is_valid_combination([player_hand[i], player_hand[j]]):
                    # 出这些牌
                    self.add_to_game_area(player_hand, [player_hand[i], player_hand[j]])
                    return
        #检查卡池中是否有有效组合
        for i in range(len(self.placement_slots)):
            for j in range(i + 1, len(self.placement_slots)):
                if self.is_valid_combination([self.placement_slots[i], self.placement_slots[j]]):           
                    self.add_to_game_area(player_hand, [self.placement_slots[i], self.placement_slots[j]])
                    return
        # 如果没有有效组合，随机抽一张牌
        if self.public_pouch:
            player_hand.append(self.public_pouch.pop())

    def is_row_valid(self, cards, start_index):
        if start_index >= len(cards):
            return True  # 已经检查完所有卡牌

        for end_index in range(start_index + 2, len(cards)):
            if self.is_valid_combination(cards[start_index:end_index + 1]):
                if self.is_row_valid(cards, end_index + 1):
                    return True
        return False


def is_in_middle_area(card, placement_slots, card_display_width, card_display_height, cards):
    card_rect = pygame.Rect(card.x, card.y, card_display_width, card_display_height)
    for slot in placement_slots:
        if slot.contains(card_rect):
            print(f"Card in middle area: {card.filename()}, position: {card.x}, {card.y}")
            return True, cards.index(card) if card in cards else None
    return False, None




def draw_start_screen(screen, font, title_font):
    white = (255, 255, 255)
    blue = (0, 0, 255)

    background_image = pygame.image.load('pics/background.jpg')
    screen.fill(white)
    screen.blit(background_image, (0, 50))

    title_text = title_font.render("Rummikub", True, white)
    title_rect = title_text.get_rect(center=(600, 300))
    screen.blit(title_text, title_rect)

    start_button = pygame.Rect(520, 500, 160, 50)
    pygame.draw.rect(screen, blue, start_button)
    start_text = font.render('Start', True, white)
    screen.blit(start_text, (start_button.x + 50, start_button.y + 15))

    return start_button
def main():
    pygame.init()
    screen = pygame.display.set_mode((1200, 1000))
    pygame.display.set_caption("Rummikub Game")

    game = RummikubGame()
    game.start_game()

    font = pygame.font.Font(None, 36)
    title_font = pygame.font.Font(None, 150)

    timer_font = pygame.font.Font(None, 36)
    timer_start = pygame.time.get_ticks()
    timer_duration = 60000
    timer_rect = pygame.Rect(1000, 550, 110, 40)

    show_button = pygame.Rect(1000, 600, 100, 40)
    show_text = font.render('Show', True, (255, 255, 255))
    show_cards = False

    done_button = pygame.Rect(1000, 700, 100, 40)
    done_text = font.render('Done', True, (255, 255, 255))

    robot_play_button = pygame.Rect(1000, 650, 100, 40)
    robot_play_text = font.render('Robot', True, (255, 255, 255))

    card_display_width, card_display_height = 70, 90
    Card.load_images(card_display_width, card_display_height)

    cardBackOriginal = pygame.image.load('pics/tileBack.png')
    cardBack = pygame.transform.scale(cardBackOriginal, (card_display_width, card_display_height))
    cardBackPos = (1100, 650)
    cardDeckRect = cardBack.get_rect(topleft=cardBackPos)

    cards = []
    choosing_tiles = False  # 初始化choosing_tiles变量

    dragging = False
    selected_card = None

    placement_slots = []
    for row in range(5):
        for col in range(12):
            x = 200 + col * card_display_width
            y = 100 + row * card_display_height
            slot = pygame.Rect(x, y, card_display_width, card_display_height)
            placement_slots.append(slot)

    board_background_original = pygame.image.load('pics/board.png')
    board_background = pygame.transform.scale(board_background_original, (card_display_width + 5, card_display_height))

    hand_area_slots = [pygame.Rect(x, y, card_display_width, card_display_height)
                       for y in [750, 800]
                       for x in range(50, 1150, card_display_width + 5)]
    for i, card in enumerate(game.players[game.current_player]):
        card.setPosition(hand_area_slots[i].x, hand_area_slots[i].y)

    left_hand_area_slots = [pygame.Rect(0, y, card_display_width, card_display_height) 
                            for y in range(0, 900, card_display_height + 5)]

    right_hand_area_slots = [pygame.Rect(1150, y, card_display_width, card_display_height) 
                             for y in range(0, 900, card_display_height + 5)]

    top_hand_area_slots = [pygame.Rect(x, 30, card_display_width, card_display_height) 
                           for x in range(50, 1150, card_display_width + 5)]

    main_background = pygame.image.load('pics/background2.png')
    main_background = pygame.transform.scale(main_background, (1200, 1000))

    start_screen = True
    while start_screen:
        start_button = draw_start_screen(screen, font, title_font)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if start_button.collidepoint((mx, my)):
                    start_screen = False
        pygame.display.flip()

    running = True
    while running:
        screen.blit(main_background, (0, 0))
        need_update = False

        current_time = pygame.time.get_ticks()
        time_left = max(timer_duration - (current_time - timer_start), 0)
        timer_text = timer_font.render(f'Time: {time_left // 1000}', True, (255, 255, 255))
        screen.fill((0, 128, 0), timer_rect)
        screen.blit(timer_text, (timer_rect.x + 10, timer_rect.y + 10))
        pygame.display.update(timer_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if robot_play_button.collidepoint((mx, my)):
                    robot_play_turn(game, game.current_player)
                    game.current_player = (game.current_player + 1) % len(game.players)

                if cardDeckRect.collidepoint((mx, my)) and not choosing_tiles:
                    drawn_tiles = game.draw_two_tiles()
                    if drawn_tiles != [None, None]:
                        choosing_tiles = True
                        cards.extend(drawn_tiles)

                if choosing_tiles:
                    for tile in drawn_tiles:
                        if tile and tile.get_scaled_rect(card_display_width, card_display_height).collidepoint((mx, my)):
                            chosen_tile = tile
                            unchosen_tile = drawn_tiles[0] if drawn_tiles[1] == chosen_tile else drawn_tiles[1]
                            if unchosen_tile is not None:
                                game.public_pouch.append(unchosen_tile)
                                random.shuffle(game.public_pouch)
                            cards.remove(unchosen_tile)
                            drawn_tiles = []
                            choosing_tiles = False

                if done_button.collidepoint((mx, my)):
                    middle_area_cards = [card for card in cards if is_in_middle_area(card, placement_slots, card_display_width, card_display_height, cards)]
                    middle_area_cards = [card for card in cards if is_in_middle_area(card, placement_slots, card_display_width, card_display_height, cards)]

                    # 初始化valid_combinations变量
                    valid_combinations = False

                    # 检查中间区域是否有卡牌
                    if not middle_area_cards:
                        print("Invalid combination. No cards in the middle area.")
                    else:
                        rows = groupby(sorted(middle_area_cards, key=lambda c: (c.y, c.x)), key=lambda c: c.y)
                        valid_combinations = True

                        for _, row_cards in rows:
                            row_cards_sorted = sorted(row_cards, key=lambda c: c.x)
                            if not game.is_row_valid(row_cards_sorted, 0):
                                valid_combinations = False
                                break

                    if valid_combinations:
                        print("Valid combination!")
                        game.current_player = (game.current_player + 1) % len(game.players)
                    else:
                        print("Invalid combination.")

                if show_button.collidepoint((mx, my)):
                    show_cards = not show_cards

                current_player_hand = game.players[game.current_player]
                all_cards = current_player_hand + cards
                for card in all_cards:
                    if card.get_scaled_rect(card_display_width, card_display_height).collidepoint((mx, my)):
                        dragging = True
                        selected_card = card

            if event.type == pygame.MOUSEBUTTONUP:
                dragging = False
                if selected_card:
                    in_middle_area = False  
                    in_hand_area = False

                    # 检查是否在中心区域的slot中
                    for slot in placement_slots:
                        if slot.collidepoint((mx, my)):
                            selected_card.setPosition(slot.x, slot.y)
                            in_middle_area = True
                            if selected_card not in cards:
                                cards.append(selected_card)
                            break

                    # 检查是否在手牌区域的slot中
                    if not in_middle_area:
                        for slot in hand_area_slots:
                            if slot.collidepoint((mx, my)):
                                selected_card.setPosition(slot.x, slot.y)
                                in_hand_area = True
                                if selected_card in cards:
                                    cards.remove(selected_card)
                                if selected_card not in game.players[game.current_player]:
                                    game.players[game.current_player].append(selected_card)
                                break

                    # 如果不在任何区域，则从cards列表中移除
                    if not in_middle_area and not in_hand_area and selected_card in cards:
                        cards.remove(selected_card)

                    selected_card = None
                    need_update = True


            if event.type == pygame.MOUSEMOTION and dragging:
                mx, my = pygame.mouse.get_pos()
                selected_card.setPosition(mx - card_display_width / 2, my - card_display_height / 2)
                print(f"Dragging card to position: {selected_card.x}, {selected_card.y}")

            if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION]:
                need_update = True

        for card in cards:
            if card and not choosing_tiles:
                card_image, card_rect = card.get_scaled_image(card_display_width, card_display_height)
                screen.blit(card_image, card_rect)
            elif card and choosing_tiles and card in drawn_tiles:
                card_image, card_rect = card.get_scaled_image(card_display_width, card_display_height)
                screen.blit(card_image, card_rect)

        for slot in hand_area_slots:
            screen.blit(board_background, (slot.x, slot.y))

        screen.blit(cardBack, cardBackPos)

        for slot in placement_slots + hand_area_slots:
            pygame.draw.rect(screen, (200, 200, 200), slot, 1)

        for slot in left_hand_area_slots + right_hand_area_slots + top_hand_area_slots:
            screen.blit(board_background, (slot.x, slot.y))

        for card in cards:
            card_image, card_rect = card.get_scaled_image(card_display_width, card_display_height)
            screen.blit(card_image, card_rect)

        for i in range(1, len(game.players)):
            robot_hand = game.players[i]
            for j, card in enumerate(robot_hand):
                if i == 1:
                    x, y = left_hand_area_slots[j].x, left_hand_area_slots[j].y
                elif i == 2:
                    x, y = top_hand_area_slots[j].x, top_hand_area_slots[j].y
                elif i == 3:
                    x, y = right_hand_area_slots[j].x, right_hand_area_slots[j].y

                if show_cards:
                    card_image, _ = card.get_scaled_image(card_display_width, card_display_height)
                else:
                    card_image = Card.loaded_images['back']

                screen.blit(card_image, (x, y))

        pygame.draw.rect(screen, (0, 128, 0), robot_play_button)
        screen.blit(robot_play_text, (robot_play_button.x + 10, robot_play_button.y + 10))

        pygame.draw.rect(screen, (0, 128, 0), done_button)
        screen.blit(done_text, (1020, 710))

        pygame.draw.rect(screen, (0, 128, 0), show_button)
        screen.blit(show_text, (show_button.x + 10, show_button.y + 10))

        for card in game.players[game.current_player]:
            card_image, card_rect = card.get_scaled_image(card_display_width, card_display_height)
            screen.blit(card_image, card_rect)

        if need_update:
            pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()
