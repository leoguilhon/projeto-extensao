import type { ReactNode } from "react";

interface ActionMenuProps {
  children: ReactNode;
  label?: string;
}

export function ActionMenu({ children, label = "⚙️" }: ActionMenuProps) {
  return (
    <details className="action-menu">
      <summary>{label}</summary>
      <div className="action-menu-panel">{children}</div>
    </details>
  );
}
