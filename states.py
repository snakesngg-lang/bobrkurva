from aiogram.fsm.state import State, StatesGroup


class ApplicationForm(StatesGroup):
    choosing_game = State()
    entering_subscribers = State()
    entering_videos_per_day = State()
    choosing_goal = State()
    entering_custom_goal = State()
    uploading_screenshot = State()
