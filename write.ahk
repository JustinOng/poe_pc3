SendMode Input
SetTitleMatchMode, 1
SetKeyDelay, 0

ifWinActive, Path of Exile
{
    SendInput {Enter}%1%{Enter}
}