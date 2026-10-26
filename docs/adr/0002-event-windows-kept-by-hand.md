---
status: accepted
---
# Seasonal Event windows are kept by hand in the code

A seasonal Event (the Trick-or-Treat Event, the Christmas and Spring ones) runs beside the Star Paths with
its own Duties. The save keeps those Duties only as achievements (an id, a count and the last milestone
claimed); their names, what they ask and their milestones are in the game's data files, which
`tools/gen_event_duties.py` bakes into `ddvhud/event_duty_data.py` as ADR-0001 does for Rewards. But which
Event is on, and until when, the game learns from its servers each session and never writes to the save or
to any file on disk: the achievements for every past and future Event sit in the save all year, at their
old counts. So `ddvhud/event_duties.EVENTS` lists each Event's window by hand, and the HUD shows an Event's
Duties only inside it. Consequence: a new run of an Event needs its dates added before the HUD lists it,
and a wrong end time hides or keeps the Duties for a few hours at the edge. The alternative, showing an
Event whenever one of its Duties has progress, would keep last year's half-done Duties on the list forever.
