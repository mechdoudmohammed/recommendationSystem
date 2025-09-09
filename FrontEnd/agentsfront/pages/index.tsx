import Image from "next/image";
import localFont from "next/font/local";
import Header from '@/components/header'
import NavBar from '@/components/NavBar'
import Categories from '@/components/Categories'
import ProductCard from '@/components/ProductCard'
const style = {
  wrapper: `w-full flex h-full w-full overflow-hidden flex-col bg-[#F0F2F5] text-white`,
  main: 'sm-mx-auto sm:mt-1 mt-14 sm:mt-0 md:flex  overflow-hidden   bg-[#F0F2F5]  py-7 md:py-12  ',
  content: `  flex-col    md:w-full  lg:w-full overflow-hidden `,
  infoContainer: `hidden sm:pl-16   w-1/4 lg:block bg-[#F0F2F5] `,
}

export default function Home() {

  const data = [
    {
      'title':'Apple Watch Series 7 GPS, Aluminium Case, Starlight Sport',
      'product_img':'/images/watch.png'
    },
    {
      'title':'Apple Watch Series 7 GPS, Aluminium Case, Starlight Sport',
      'product_img':'/images/watch.png'
    },
    {
      'title':'Apple Watch Series 7 GPS, Aluminium Case, Starlight Sport',
      'product_img':'/images/watch.png'
    },
    {
      'title':'Apple Watch Series 7 GPS, Aluminium Case, Starlight Sport',
      'product_img':'/images/watch.png'
    },
    {
      'title':'Apple Watch Series 7 GPS, Aluminium Case, Starlight Sport',
      'product_img':'/images/watch.png'
    },
    {
      'title':'Apple Watch Series 7 GPS, Aluminium Case, Starlight Sport',
      'product_img':'/images/watch.png'
    },
    {
      'title':'Apple Watch Series 7 GPS, Aluminium Case, Starlight Sport',
      'product_img':'/images/watch.png'
    },
    {
      'title':'Apple Watch Series 7 GPS, Aluminium Case, Starlight Sport',
      'product_img':'/images/watch.png'
    },
    {
      'title':'Apple Watch Series 7 GPS, Aluminium Case, Starlight Sport',
      'product_img':'/images/watch.png'
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

          <NavBar />
          <Categories />
          <div className="px-24 mt-4">
            <h1 className="text-2xl font-nunito text-black font-bold">More to Love</h1>
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
              ):(
                <div>Loding....</div>
              )
            }
            
          </div>

        </div>



      </div>
    </div>
  )
}
