import main


def test_chat_handles_reset_and_exit_commands(make_bot, monkeypatch, capsys):
    bot = make_bot(["Use colchetes."])
    typed = iter(["Como criar uma lista?", "/limpar", "/sair"])
    monkeypatch.setattr("builtins.input", lambda _: next(typed))

    main.run_chat(bot)

    output = capsys.readouterr().out
    assert "Use colchetes." in output
    assert "Histórico limpo." in output
    assert "Até mais!" in output
    assert bot.history == []


def test_chat_ignores_empty_input(make_bot, monkeypatch):
    bot = make_bot(["resposta"])
    typed = iter(["", "   ", "/sair"])
    monkeypatch.setattr("builtins.input", lambda _: next(typed))

    main.run_chat(bot)

    assert bot.history == []