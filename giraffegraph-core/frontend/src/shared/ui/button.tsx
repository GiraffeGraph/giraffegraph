import Link from "next/link";
import type { ButtonHTMLAttributes, ReactNode } from "react";

import { Icon, type IconName } from "@/shared/ui/icons";

type Variant = "primary" | "secondary" | "quiet";
type Size = "md" | "sm";

function classes(variant: Variant, size: Size, busy: boolean, extra?: string): string {
  return [
    "button",
    `button-${variant}`,
    size === "sm" ? "button-sm" : "",
    busy ? "is-busy" : "",
    extra ?? "",
  ]
    .filter(Boolean)
    .join(" ");
}

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
  /** Shows a spinner, blocks clicks and tells assistive technology the action is running. */
  busy?: boolean;
  icon?: IconName;
  iconAfter?: IconName;
  children: ReactNode;
}

export function Button({
  variant = "secondary",
  size = "md",
  busy = false,
  icon,
  iconAfter,
  className,
  disabled,
  type = "button",
  children,
  ...rest
}: ButtonProps) {
  return (
    <button
      {...rest}
      type={type}
      className={classes(variant, size, busy, className)}
      disabled={disabled || busy}
      aria-busy={busy || undefined}
    >
      {busy ? <span className="spinner" aria-hidden="true" /> : icon ? <Icon name={icon} /> : null}
      {children}
      {iconAfter && !busy ? <Icon name={iconAfter} /> : null}
    </button>
  );
}

export function ButtonLink({
  href,
  variant = "secondary",
  size = "md",
  icon,
  iconAfter,
  className,
  children,
}: {
  href: string;
  variant?: Variant;
  size?: Size;
  icon?: IconName;
  iconAfter?: IconName;
  className?: string;
  children: ReactNode;
}) {
  return (
    <Link href={href} className={classes(variant, size, false, className)}>
      {icon ? <Icon name={icon} /> : null}
      {children}
      {iconAfter ? <Icon name={iconAfter} /> : null}
    </Link>
  );
}
