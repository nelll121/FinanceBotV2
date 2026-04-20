"""utils/middlewares.py placeholder."""
    """Allow command handling for registered users only (except /start and active registration FSM)."""
        fsm = data.get("state")
        if fsm is not None:
            current_state = await fsm.get_state()
            if current_state is not None:
                return await handler(event, data)

