export function getMeetingDetailsPath(clubId: string | number, meetingId: string | number) {
  return `/clubs/${clubId}/meetings/${meetingId}`;
}

export function isInteractiveElementTarget(target: EventTarget | null) {
  return target instanceof HTMLElement && Boolean(target.closest("a, button, input, textarea, select"));
}

export function formatMeetingDateTime(value: string) {
  return new Date(value).toLocaleString("pt-BR", {
    dateStyle: "short",
    timeStyle: "short",
  });
}

export function formatMeetingDay(value: string) {
  return new Date(value).toLocaleDateString("pt-BR", {
    day: "2-digit",
    month: "short",
    weekday: "short",
  });
}

export function formatMeetingTime(value: string) {
  return new Date(value).toLocaleTimeString("pt-BR", {
    hour: "2-digit",
    minute: "2-digit",
  });
}
