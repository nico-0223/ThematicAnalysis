import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <div className="flex min-h-[60vh] items-center justify-center">
      <div className="text-center">
        <p className="text-3xl font-semibold">404</p>
        <p className="text-sm text-muted-foreground mt-1">Page not found.</p>
        <Link to="/" className="mt-4 inline-block text-sm underline">Back to dashboard</Link>
      </div>
    </div>
  );
}
