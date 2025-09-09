

const Header = () => {


    return (
        <div className='bg-[#131921] pt-6 space-x-2 flex h-24 px-20 w-full'>


            <div className='flex w-auto    justify-center items-center'>
                <div className="grid grid-cols-6 gap-12">
                    <div className="flex bg-[#535353] px-2 rounded-full space-x-2 items-center">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="white" id="Outline" viewBox="0 0 24 24" width="20px" height="20pxs"><path d="M7,0H4A4,4,0,0,0,0,4V7a4,4,0,0,0,4,4H7a4,4,0,0,0,4-4V4A4,4,0,0,0,7,0ZM9,7A2,2,0,0,1,7,9H4A2,2,0,0,1,2,7V4A2,2,0,0,1,4,2H7A2,2,0,0,1,9,4Z" /><path d="M20,0H17a4,4,0,0,0-4,4V7a4,4,0,0,0,4,4h3a4,4,0,0,0,4-4V4A4,4,0,0,0,20,0Zm2,7a2,2,0,0,1-2,2H17a2,2,0,0,1-2-2V4a2,2,0,0,1,2-2h3a2,2,0,0,1,2,2Z" /><path d="M7,13H4a4,4,0,0,0-4,4v3a4,4,0,0,0,4,4H7a4,4,0,0,0,4-4V17A4,4,0,0,0,7,13Zm2,7a2,2,0,0,1-2,2H4a2,2,0,0,1-2-2V17a2,2,0,0,1,2-2H7a2,2,0,0,1,2,2Z" /><path d="M20,13H17a4,4,0,0,0-4,4v3a4,4,0,0,0,4,4h3a4,4,0,0,0,4-4V17A4,4,0,0,0,20,13Zm2,7a2,2,0,0,1-2,2H17a2,2,0,0,1-2-2V17a2,2,0,0,1,2-2h3a2,2,0,0,1,2,2Z" /></svg>
                        <select class=" focus:outline-none justify-center bg-[#535353]  items-center flex  h-12 w-auto rounded-full">
                            <option value="option1">All Categories</option>
                            <option value="option2">Option 2</option>
                            <option value="option3">Option 3</option>
                        </select>
                    </div>


                    <div className="p-2 px-4 rounded-full hover:bg-gray-800 hover:cursor-pointer">
                        <h1 className="text-[18px] font-nunito">Bundle deals</h1>
                    </div>

                    <div className="p-2 px-4 rounded-full hover:bg-gray-800 hover:cursor-pointer">
                        <h1 className="text-[18px] font-nunito">Weekly deals</h1>
                    </div>
                    <div className="p-2 px-4 rounded-full hover:bg-gray-800 hover:cursor-pointer">
                        <h1 className="text-[18px] font-nunito">Top Brands</h1>
                    </div>
                    <div className="p-2 px-4 rounded-full hover:bg-gray-800 hover:cursor-pointer">
                        <h1 className="text-[18px] font-nunito">Bestsellers</h1>
                    </div>
                    <div className="p-2 px-4 rounded-full hover:bg-gray-800 hover:cursor-pointer">
                        <h1 className="text-[18px] font-nunito">more</h1>
                    </div>

                </div>

            </div>
        </div>
    )
}

export default Header;