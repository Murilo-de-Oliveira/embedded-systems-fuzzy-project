import { type ReactNode } from 'react';
import { GlobalHeaderWrapper } from '../components/common/GlobalHeaderWrapper';

interface LayoutProps {
  children: ReactNode;
}

export const Layout = ({ children }: LayoutProps) => {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-black/90">
      <GlobalHeaderWrapper />
      <main className="container mx-auto p-4 mt-4">{children}</main>
    </div>
  );
};
