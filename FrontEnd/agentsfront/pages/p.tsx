import Image from "next/image";
import localFont from "next/font/local";
import Header from '@/components/header'
import NavBar from '@/components/NavBar'
import Categories from '@/components/Categories'
import ProductCard from '@/components/ProductCard'
const style = {
    wrapper: `w-full flex h-full w-full overflow-hidden flex-col bg-white text-white`,
    main: 'sm-mx-auto sm:mt-1 mt-14 sm:mt-0 md:flex  overflow-hidden   bg-white  py-7 md:py-12  ',
    content: `  flex-col    md:w-full  lg:w-full overflow-hidden `,
    infoContainer: `hidden sm:pl-16   w-1/4 lg:block bg-[#F0F2F5] `,
}

export default function Product() {

    const data = [
        {
            'title': 'Apple Watch Series 7 GPS, Aluminium Case, Starlight Sport',
            'product_img': '/images/watch.png'
        },
        {
            'title': 'Apple Watch Series 7 GPS, Aluminium Case, Starlight Sport',
            'product_img': '/images/watch.png'
        },
        {
            'title': 'Apple Watch Series 7 GPS, Aluminium Case, Starlight Sport',
            'product_img': '/images/watch.png'
        },
        {
            'title': 'Apple Watch Series 7 GPS, Aluminium Case, Starlight Sport',
            'product_img': '/images/watch.png'
        },
        {
            'title': 'Apple Watch Series 7 GPS, Aluminium Case, Starlight Sport',
            'product_img': '/images/watch.png'
        },
        {
            'title': 'Apple Watch Series 7 GPS, Aluminium Case, Starlight Sport',
            'product_img': '/images/watch.png'
        },
        {
            'title': 'Apple Watch Series 7 GPS, Aluminium Case, Starlight Sport',
            'product_img': '/images/watch.png'
        },
        {
            'title': 'Apple Watch Series 7 GPS, Aluminium Case, Starlight Sport',
            'product_img': '/images/watch.png'
        },
        {
            'title': 'Apple Watch Series 7 GPS, Aluminium Case, Starlight Sport',
            'product_img': '/images/watch.png'
        },

    ]
    console.log(data)

    return (
        <div className={style.wrapper}>
            <Header />
            <div className={style.main}>
                {/* <div className='hidden  sm:pr-4 lg:w-1/4 md:w-1/3 md:block  bg-'>
          <div className='flex  overflow-y-scroll  justify-end'></div>

        </div> */}
                <div className={style.content}>



                    <section className="w-full space-x-4 h-ful mt-10 flex px-20">
                        <div className="w-1/3">
                            <img className="p-8 border w-full rounded-t-lg" src='/images/watch.png' alt="product image" />

                        </div>
                        <div className="w-1/3 flex-col ">
                            <h1 className="text-[40px] font-bold text-black">MAD93.85</h1>
                            <div className="flex space-x-2 pb-2">
                                <h1 className="text-gray-400 text-[20px]">MAD144.38</h1>
                                <h1 className="text-red-600 text-[20px]">35% off</h1>
                            </div>
                            <h1 className="text-black text-[15px] font-bold w-full">New Men Shoulder Bags Chest Bag Multifuncional Crossbody Bags Travel Sling Bag Men's Chest Bag Cross Body Chest Bag for Men Bag</h1>
                            <h1 className="text-[12px] text-gray-600">249 Reviews ౹ 2,000+ sold</h1>
                        </div>
                        <div className="w-1/3">
                            <div className="border border-gray-400 space-y-2 rounded-lg p-4">
                                <section className="w-full flex justify-between">
                                    <h1 className="text-black font-bold text-sm">Ship to</h1>
                                    <h1 className="text-black font-bold text-sm">Morocco</h1>
                                </section>
                                <div>
                                    <h1 className="text-black font-bold text-[15px]">Free shipping over MAD106.60</h1>
                                </div>
                                <div className="flex space-x-2">
                                    <h1 className="text-gray-600 text-[15px] ">Delivery:</h1>
                                    <h1 className="text-black font-bold text-[15px]">Nov. 25 - Dec. 03 </h1>
                                </div>
                                <div className="flex-col space-x-2">

                                    <h1 className="text-black font-bold text-[14px]">Security & Privacy </h1>
                                    <h1 className="text-gray-600 text-[12px] ">Safe payments: We do not share your personal details with any third parties without your consent.
                                        Secure personal details: We protect your privacy and keep your personal details safe and secure.</h1>
                                </div>

                                <hr className=" " />

                                <button className="bg-[#D3031C] w-full py-2 font-bold text-[16px] rounded-full">
                                    Buy now
                                </button>

                                <button className="border-1 border border-black text-black w-full py-2 font-bold text-[16px] rounded-full">
                                    Add to cart
                                </button>

                            </div>

                        </div>

                    </section>

                    <section>
                        <div className="px-20">
                            <h1 className="text-2xl font-nunito text-black font-bold">Related items</h1>
                        </div>

                        <div className="w-full mt-4 grid grid-cols-4 gap-4 px-24">
                            {
                                data ? (
                                    data.map((product, index) => (
                                        <ProductCard
                                            key={index}
                                            data={product}
                                        />
                                    ))
                                ) : (
                                    <div>Loding....</div>
                                )
                            }

                        </div>
                    </section>

                </div>



            </div>
        </div>
    )
}
