
import dynamic from "next/dynamic";
import Link from 'next/link';

const style = {
  header: 'fixed inset-0 z-50 w-full flex flex-col h-16 bg-[#131921] ',
  wrapper: 'flex justify-between px-2 sm:px-24 items-center  h-full border-b-[#343536]  lg:ml-2',
  leftHeader: 'flex  items-center  ',
  rightHeader: 'flex items-center ',
  profileImageContainer:
    'flex h-9 w-9 cursor-pointer items-center justify-center overflow-hidden rounded-full relative',
  profileImage: 'object-contain',
  logo: 'hidden lg:flex h-10 w-15 items-center ',
}

const Header = () => {


  return (
    <header className={style.header}>
      <div className={style.wrapper}>
        <div className={style.leftHeader}>
          <Link href='/' className="flex space-x-2 items-center pr-6">
            <img className='hidden lg:flex h-10 w-15 items-center ' src="images/logo.png" />
            {/* <h1 className="text-white font-bold">NovaShop</h1> */}
          </Link>
          <div className="bg-white h-11 items-center justify-center flex rounded-full w-[600px]">
            <input type="search" id="input-group-search" className=" w-full  px-6 text-sm text-gray-900   focus:outline-none   rounded-lg   " placeholder="Search for a product" />

          </div>
          <div className="bg-white h-auto ml-2 items-center justify-center flex rounded-full w-auto p-2">
            <svg xmlns="http://www.w3.org/2000/svg" id="Isolation_Mode" fill="#131921" data-name="Isolation Mode" viewBox="0 0 24 24" width="28px" height="28px"><path d="M18.9,16.776A10.539,10.539,0,1,0,16.776,18.9l5.1,5.1L24,21.88ZM10.5,18A7.5,7.5,0,1,1,18,10.5,7.507,7.507,0,0,1,10.5,18Z" /></svg>

          </div>
        </div>

        <div className={style.rightHeader}>
          {/* <div className="flex items-center">
            <img className="w-[35px] h-[35px] rounded-full" src="images/profile.jpeg" />
          </div> */}
           <div className="pl-2 flex space-x-2 items-center">
            <img src="icons/morocco.png" className="w-[28px] h-[28px]"/>
            <div className="flex-col ">
              <h1 className="text-white font-nunito leading-tight text-[12px] ">EN/</h1>
              <h1 className="text-white underline-offset-2 hover:underline hover:cursor-pointer font-nunito leading-tight font-semibold text-[12px]">MAD</h1>
            </div>
          </div>
          <div className="flex pl-4 space-x-2 items-center">
            <svg xmlns="http://www.w3.org/2000/svg" fill="white" id="Outline" viewBox="0 0 24 24" width="28px" height="28px"><path d="M12,12A6,6,0,1,0,6,6,6.006,6.006,0,0,0,12,12ZM12,2A4,4,0,1,1,8,6,4,4,0,0,1,12,2Z" /><path d="M12,14a9.01,9.01,0,0,0-9,9,1,1,0,0,0,2,0,7,7,0,0,1,14,0,1,1,0,0,0,2,0A9.01,9.01,0,0,0,12,14Z" /></svg>
            <div className="flex-col ">
              <h1 className="text-white font-nunito leading-tight text-[12px] ">Welcome</h1>
              <h1 className="text-white underline-offset-2 hover:underline hover:cursor-pointer font-nunito leading-tight font-semibold text-[12px]">Sign in / Register</h1>
            </div>
          </div>
          <div className="flex space-x-2 pl-4  items-center">
            <svg xmlns="http://www.w3.org/2000/svg" fill="white" id="Layer_1" data-name="Layer 1" viewBox="0 0 24 24" width="28px" height="28px"><path d="M23.32,4.1c-.57-.7-1.42-1.1-2.32-1.1H7.24l-.04-.35c-.18-1.51-1.46-2.65-2.98-2.65h-1.22c-.55,0-1,.45-1,1s.45,1,1,1h1.22c.51,0,.93,.38,.99,.88l1.38,11.7c.3,2.52,2.43,4.42,4.97,4.42h8.44c.55,0,1-.45,1-1s-.45-1-1-1H11.56c-1.29,0-2.41-.82-2.83-2h9.43c2.38,0,4.44-1.69,4.9-4.02l.88-4.39c.18-.88-.05-1.79-.62-2.49Zm-1.34,2.1l-.88,4.39c-.28,1.4-1.52,2.41-2.94,2.41H8.42l-.94-8h13.52c.3,0,.58,.13,.77,.37,.19,.23,.27,.54,.21,.83Zm-10.98,15.8c0,1.1-.9,2-2,2s-2-.9-2-2,.9-2,2-2,2,.9,2,2Zm9,0c0,1.1-.9,2-2,2s-2-.9-2-2,.9-2,2-2,2,.9,2,2ZM0,6c0-.55,.45-1,1-1h1.54c.55,0,1,.45,1,1s-.45,1-1,1H1c-.55,0-1-.45-1-1Zm0,4c0-.55,.45-1,1-1H3c.55,0,1,.45,1,1s-.45,1-1,1H1c-.55,0-1-.45-1-1Zm5,4c0,.55-.45,1-1,1H1c-.55,0-1-.45-1-1s.45-1,1-1h3c.55,0,1,.45,1,1Z" /></svg>
            <div className="flex-col ">
              <h1 className="text-black font-nunito leading-tight text-sm rounded-full bg-white items-center flex justify-center ">0</h1>
              <h1 className="text-white font-nunito leading-tight font-bold text-[14px]">Cart</h1>
            </div>
          </div>

        </div>
      </div>

    </header>
  )
}


export default dynamic(() => Promise.resolve(Header), { ssr: false })

