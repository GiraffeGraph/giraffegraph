import { ProjectShell } from "@/modules/projects/components/project-shell";

export default function ProjectLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <ProjectShell>{children}</ProjectShell>;
}
