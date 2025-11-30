import { Topbar } from './Topbar';

export const GlobalHeaderWrapper = () => {
  return (
    <div className="pt-4 px-4 sm:px-8 md:px-16 lg:px-24">
      <header
        className="
          w-full 
          border 
          bg-background/90 
          backdrop-blur-lg 
          shadow-xl 
          rounded-xl 
          transition-all duration-300
        "
      >
        <Topbar />
      </header>
    </div>
  );
};
